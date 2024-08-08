"""TVSD CLI entry point, main app module."""

import logging
import os
import shutil
from typing import Optional

import typer

# from docstring_parser import parse
from rich import print as rprint

from tvsd import __app_name__, __version__, app
from tvsd.actions import list_shows_as_table, search_media_and_download
from tvsd.config import register_validators, settings, update_settings_path, validate_config

# from tvsd.config import apply_config, validate_config_file
from tvsd.utils import video_in_dir

from .utils import typer_easy_cli


def _version_callback(value: bool) -> None:
    """
    Print the current version of the application and exit.

    Args:
        value (bool): A boolean value indicating whether to print the version or not.

    Returns:
        None
    """
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@typer_easy_cli
@app.callback()
def callback(
    *,
    _: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
    verbose: Optional[bool] = False,
    series_dir: Optional[str] = typer.Option(
        None,
        "--series-dir",
        "-sd",
        help="Specify the series directory, overrides config file",
    ),
    media_root: Optional[str] = typer.Option(
        None,
        "--media-root",
        "-mr",
        help="Specify the media root, overrides config file",
    ),
    env: Optional[str] = typer.Option(
        None, "--env", "-e", help="Specify the environment"
    ),
    dry_run: Optional[bool]=typer.Option(
        False,
        "--dry-run"
    )
) -> None:
    """
    Entry point for the TVSD CLI application.

    This function initializes the config file before setting instance level.
    It applies the config and sets the state of the application based on the provided options.

    Args:
        verbose (bool, optional): Show verbose output.
        series_dir (str, optional): Specify the series directory, overrides config file.
        media_root (str, optional): Specify the media root, overrides config file.
        env (str, optional): Specify the environment, overrides config file.

    Returns:
        None
    """
    register_validators()

    if env:
        # change the environment to update proper settings
        settings.setenv(env)

    # update the dynaconf settings
    if verbose:
        typer.echo("Will write verbose output")
        settings.set("verbose", True)
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if series_dir:
        settings.set("series_dir", series_dir)
        logging.info("Series directory set to %s", series_dir)

    if media_root:
        settings.set("media_root", media_root)
        logging.info("Media Root set to %s", media_root)

    if dry_run:
        settings.set("dry_run", dry_run)
        logging.info("Dry run set to %s.", dry_run)

    validate_config()


@app.command()
def search(
    query: str,
    specials_only: bool = typer.Option(
        False,
        "--specials",
        "-s",
        help="Download Specials Only",
    ),
) -> None:
    """
    Search for media and download

    Args:
        specials_only (Optional[bool], optional): Download only specials episode
        query (str): query string
    """

    # raises on first error found
    settings.validators.validate()

    search_media_and_download(query, specials_only)


@app.command()
def clean_temp() -> None:
    """
    Cleans the temp directory.

    This function validates the config file and then prompts the user to confirm
    whether they want to delete all files in the temp directory. If the user confirms,
    all files in the temp directory are deleted and a new empty directory is created.

    Raises:
        FileNotFoundError: If temp directory does not exist
    """

    validate_config()

    try:
        dir_content = os.listdir(settings.TEMP_ROOT)
        if len(dir_content) == 0:
            raise FileNotFoundError

        rprint(f"{settings.TEMP_ROOT} contents: ")
        for item in dir_content:
            rprint(f"  {item}")

        confirm: str = typer.prompt(
            text="Do you want to delete all files in temp directory?",
            type=str,
            default="n",
        )
        if confirm.capitalize() == "Y":
            if not settings.DRY_RUN:
                shutil.rmtree(settings.TEMP_ROOT, ignore_errors=True)
                os.mkdir(settings.TEMP_ROOT)
            logging.info("All files deleted")

    except FileNotFoundError:
        logging.info("Temp directory %s does not exist", settings.TEMP_ROOT)


@app.command()
def list_shows() -> None:
    """
    List all shows in the database.

    This function retrieves a list of all shows in the database and displays them in a table format.
    """
    list_shows_as_table(show_index=False)


@app.command()
def remove_show() -> None:
    """List shows and remove selected show.

    This function lists all the shows and their indices, prompts the user to select a show index to remove,
    and then removes the selected show. If the user selects an invalid index or cancels the prompt, the function
    aborts and raises a typer.Abort() exception.

    Returns:
        None
    """

    shows, num_rows = list_shows_as_table(show_index=True)

    while True:
        choice = typer.prompt(
            "Select show index to remove", type=int, default=-1, show_default=False
        )
        if choice == -1:
            typer.echo("No input received, exiting...")
            raise typer.Abort()
        if choice < num_rows:
            if typer.confirm(f"Will remove {shows[choice]}. Are you sure?", abort=True):
                typer.echo("Removing show: " + shows[choice])

                if not settings.DRY_RUN:
                    shutil.rmtree(
                        os.path.join(
                            settings.MEDIA_ROOT, settings.SERIES_DIR, shows[choice]
                        )
                    )
                typer.echo("Show removed")
            break

        typer.echo("Option out of range, please try again")


@app.command()
def print_state() -> None:
    """
    Print the current state of the application.

    This function prints the current state of the application, including all key-value pairs in the `state` dictionary.

    Raises:
        ConfigFileError: If the configuration file is invalid or missing.
    """
    # validate_config()

    data: dict = settings.as_dict(env=settings.current_env)
    data.pop("POST_HOOKS", None)
    data.pop("PRETTY_EXCEPTIONS_SHOW_LOCALS", None)

    typer.echo(data)


@typer_easy_cli
@app.command()
def clean_base(
    *,
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Interactive mode",
    ),
    greedy: bool = typer.Option(
        False,
        "--greedy",
        "-g",
        help="Remove directories without videos",
    ),
    target: str = typer.Option(
        "",
        help="Target directory",
    ),
    _no_confirm: bool = typer.Option(
        False,
        "--no-confirm",
    ),
) -> None:
    """
    Remove empty directories in the base path

    Args:
        interactive (bool, optional): Whether to run in interactive mode. Defaults to False
        greedy (bool, optional): Remove all directories without videos, even it they are not empty. Defaults to False.
        target (str, optional): Target directory. Defaults to os.path.join(settings.MEDIA_ROOT, settings.SERIES_DIR).
        _no_confirm (bool, optional): Don't show prompt to confirm actions. Defaults to False.
    """
    validate_config()

    if greedy and not _no_confirm:
        typer.confirm(
            "Greedy mode will remove directories without videos, even if they contain other content",
            abort=True,
        )

    if target == "":
        target=os.path.join(settings.MEDIA_ROOT, settings.SERIES_DIR)

    for root, dirs, _ in os.walk(target, topdown=False):
        for name in dirs:
            path: str = os.path.join(root, name)
            if not os.listdir(path) and (
                not interactive
                or typer.confirm(f"Found Empty Directory, Remove {path}?")
            ):
                # empty dir
                logging.info("Empty Directory, Removing %s", path)
                if not settings.DRY_RUN:
                    shutil.rmtree(path)
            elif (
                greedy
                and not video_in_dir(path)
                and (
                    not interactive
                    or typer.confirm(
                        f"Found Directory w/o videos and sub-dir, Remove {path}?"
                    )
                )
            ):
                # clean_base(interactive, greedy, target, _no_confirm=True)
                # # not empty dir and no video, remove
                logging.info(
                    "Directory without video and and sub-dir, Removing %s", {path}
                )
                if not settings.DRY_RUN:
                    shutil.rmtree(path)
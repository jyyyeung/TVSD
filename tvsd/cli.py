"""TVSD CLI entry point, main app module."""
import logging
import os
import shutil
from typing import Optional

import typer
from rich import print as rprint

from tvsd import __app_name__, __version__, app, state
from tvsd._variables import state_base_path, state_series_dir, state_temp_base_path
from tvsd.actions import list_shows_as_table, search_media_and_download
from tvsd.config import apply_config, validate_config_file
from tvsd.utils import video_in_dir


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
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
    base_path: Optional[str] = typer.Option(
        None,
        "--base-path",
        "-bp",
        help="Specify the base path, overrides config file",
    ),
) -> None:
    """
    Options to update state of the application.

    Args:
        _: Optional[bool]: Show the application's version and exit.
        verbose (Optional[bool], optional): Show verbose output. Defaults to False.
        series_dir (Optional[str], optional): Specify the series directory, overrides config file. Defaults to None.
        base_path (Optional[str], optional): Specify the base path, overrides config file. Defaults to None.
    """
    # initialize the config file before setting instance level
    validate_config_file()
    apply_config()

    if verbose:
        typer.echo("Will write verbose output")
        state["verbose"] = True
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if series_dir:
        state["series_dir"] = series_dir
        logging.info("Series directory set to %s", series_dir)

    if base_path:
        state["base_path"] = base_path
        logging.info("Base path set to %s", base_path)


@app.command()
def search(
    query: str,
    specials_only: bool = typer.Option(
        False,
        "--specials",
        "-s",
        help="Download Specials Only",
    ),
):
    """Search for media and download

    Args:
        specials_only (Optional[bool], optional): Download only specials episode
        query (str): query string
    """
    validate_config_file()
    search_media_and_download(query, specials_only)


@app.command()
def clean_temp():
    """
    clean_temp Cleans the temp directory

    Raises:
        FileNotFoundError: If temp directory does not exist
    """
    validate_config_file()

    try:
        dir_content = os.listdir(state_temp_base_path())
        if len(dir_content) == 0:
            raise FileNotFoundError

        rprint(f"{state_temp_base_path()} contents: ")
        for item in dir_content:
            rprint(f"  {item}")

        confirm = typer.prompt(
            text="Do you want to delete all files in temp directory?",
            type=str,
            default="n",
        )
        if confirm.capitalize() == "Y":
            shutil.rmtree(state_temp_base_path(), ignore_errors=True)
            os.mkdir(state_temp_base_path())
            logging.info("All files deleted")

    except FileNotFoundError:
        logging.info("Temp directory %s does not exist", state_temp_base_path())


@app.command()
def list_shows():
    """List all shows in the database"""
    list_shows_as_table(show_index=False)


@app.command()
def remove_show():
    """List shows and remove selected show"""

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
                shutil.rmtree(
                    os.path.join(state_base_path(), state_series_dir(), shows[choice])
                )
                typer.echo("Show removed")
            break

        typer.echo("Option out of range, please try again")


@app.command()
def print_state():
    """
    print_state Prints the state of the application
    """
    validate_config_file()

    for key, value in state.items():
        typer.echo(f"{key}: {value}")


@app.command()
def clean_base(
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
        os.path.join(state_base_path(), state_series_dir()),
        help="Target directory",
    ),
    _no_confirm: bool = typer.Option(
        False,
        "--no-confirm",
    ),
):
    """
    clean_base Remove empty directories in the base path

    Args:
        interactive (bool, optional): Whether to run in interactive mode. Defaults to False
        greedy (bool, optional): Remove all directories without videos, even it they are not empty. Defaults to False.
        target (str, optional): Target directory. Defaults to os.path.join(state_base_path(), state_series_dir()).
        _no_confirm (bool, optional): Don't show prompt to confirm actions. Defaults to False.
    """
    validate_config_file()
    if greedy and not _no_confirm:
        typer.confirm(
            "Greedy mode will remove directories without videos, even if they contain other content",
            abort=True,
        )

    for root, dirs, _ in os.walk(target, topdown=False):
        for name in dirs:
            path = os.path.join(root, name)
            if not os.listdir(path) and (
                not interactive
                or typer.confirm(f"Found Empty Directory, Remove {path}?")
            ):
                # empty dir
                logging.info("Empty Directory, Removing %s", path)
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
                shutil.rmtree(path)

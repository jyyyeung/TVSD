import logging
import os
from pathlib import Path
import shutil
from typing import Optional
from tvsd._variables import BASE_PATH, TEMP_BASE_PATH, SERIES_DIR
from tvsd import state


import typer
from rich import print as rprint


from tvsd import ERRORS, __app_name__, __version__, database, app, state
from tvsd.actions import search_media_and_download
from tvsd.config import (
    apply_config,
    init_app,
    validate_config_file,
)
from tvsd.actions import list_shows_as_table


@app.command()
def init(
    db_path: str = typer.Option(
        str(database.DEFAULT_DB_FILE_PATH),
        "--db-path",
        "-db",
        prompt="TVSD database location?",
    ),
) -> None:
    """Initialize the to-do database."""
    app_init_error = init_app(db_path)
    if app_init_error:
        typer.secho(
            f'Creating config file failed with "{ERRORS[app_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        typer.secho(
            f'Creating database failed with "{ERRORS[db_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(f"The TVSD database is {db_path}", fg=typer.colors.GREEN)


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
    """
    # initialize the config file before setting instance level
    validate_config_file()

    if verbose:
        typer.echo("Will write verbose output")
        state["verbose"] = True
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if series_dir:
        state["series_dir"] = series_dir
        logging.info(f"Series directory set to {series_dir}")

    if base_path:
        state["base_path"] = base_path
        logging.info(f"Base path set to {base_path}")


@app.command()
def search(query: str):
    """Search for media and download

    Args:
        query (str): query string
    """
    search_media_and_download(query=query)


@app.command()
def clean_temp():
    """Cleans the temp directory"""
    validate_config_file()

    try:
        dir_content = os.listdir(TEMP_BASE_PATH)
        if len(dir_content) == 0:
            raise (FileNotFoundError)
        rprint(f"{TEMP_BASE_PATH} contents: ")
        for item in dir_content:
            rprint(f"  {item}")

        confirm = typer.prompt(
            text="Do you want to delete all files in temp directory?",
            type=str,
            default="n",
        )
        if confirm.capitalize() == "Y":
            shutil.rmtree(TEMP_BASE_PATH, ignore_errors=True)
            os.mkdir(TEMP_BASE_PATH)
            logging.info("All files deleted")
    except FileNotFoundError:
        logging.info(f"Temp directory {TEMP_BASE_PATH} does not exist")


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
                shutil.rmtree(os.path.join(BASE_PATH, SERIES_DIR, shows[choice]))
                typer.echo("Show removed")
            break

        typer.echo("Option out of range, please try again")


@app.command()
def print_state():
    """Prints the state of the application"""
    validate_config_file()

    for key, value in state.items():
        typer.echo(f"{key}: {value}")

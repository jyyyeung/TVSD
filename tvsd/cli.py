import logging
import os
from pathlib import Path
import shutil
from typing import Optional

import typer
from rich import print

from tvsd import ERRORS, __app_name__, __version__, database, app, state
from tvsd.actions import search_media_and_download
from tvsd.config import init_app, TEMP_BASE_PATH, validate_config_file


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
) -> None:
    """
    Options to update state of the application.
    """
    if verbose:
        print("Will write verbose output")
        state["verbose"] = True
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


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
        print(f"{TEMP_BASE_PATH} contents: ")
        for item in dir_content:
            print(f"  {item}")

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

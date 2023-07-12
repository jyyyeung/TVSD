import os
import shutil
from typing import Optional

import typer
from rich import print

from tvsd import __app_name__, __version__
from tvsd.actions import search_media_and_download
from tvsd.utils import TEMP_BASE_PATH

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return


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
            print("All files deleted")
    except FileNotFoundError:
        print(f"Temp directory {TEMP_BASE_PATH} does not exist")

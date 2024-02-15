# -*- coding: utf-8 -*-
import logging
import os
import sys
from typing import List, Tuple

import typer
from rich.console import Console
from rich.table import Table

from tvsd import utils

from .config import settings
from .download import Download
from .search import SearchQuery
from .utils import dir_exists, is_video


def search_media_and_download(query: str, specials_only: bool = False) -> None:
    """Search for media and download

    This function searches for media based on the given query string and downloads it.
    It first checks if the base path is mounted and exits if it is not.
    Then it searches for the given query and finds the show.
    Finally, it starts a guided download of the chosen show.

    Args:
        query (str): query string
        specials_only (bool): Download only specials episode. Defaults to False.
    """

    if not dir_exists(
        path=settings.MEDIA_ROOT, create_if_not=settings.CREATE_MEDIA_ROOT
    ):
        raise typer.Exit(code=1)

    logging.debug("Media Root: %s", settings.MEDIA_ROOT)

    if not dir_exists(path=settings.TEMP_ROOT, create_if_not=settings.CREATE_TEMP_ROOT):
        raise typer.Exit(code=1)

    logging.debug("Temp Root: %s", settings.TEMP_ROOT)

    # Search
    query_instance = SearchQuery(query)
    logging.info("Searching for %s...", query)
    query_instance.find_show()

    # Download
    download_instance = Download(
        target=query_instance.chosen_show,
        specials_only=specials_only,
    )
    logging.info("Starting %s guided download...", query_instance.chosen_show.title)
    download_instance.guided_download()


def list_shows_as_table(show_index=False) -> Tuple[List[str], int]:
    """List all shows in base directory as a table

    Args:
        show_index (bool, optional): Whether to print the row index as the first column, useful for selection. Defaults to False.

    Returns:
        Tuple[List[str], int]: List of shows and number of shows
    """
    series_path = os.path.join(settings.MEDIA_ROOT, settings.SERIES_DIR)
    logging.info("Checking if %s exists...", series_path)
    if not os.path.isdir(series_path):
        logging.error("%s does not exist! Nothing to list. Exiting...", series_path)
        sys.exit()

    console = Console()
    table = Table("Name", "Year", "#Seasons", "#Episodes")
    shows = []
    num_shows = 0
    if show_index:
        table = Table("#", "Name", "Year", "#Seasons", "#Episodes")

    for show in os.listdir(os.path.join(settings.MEDIA_ROOT, settings.SERIES_DIR)):
        num_files = 0
        num_seasons = 0
        if not os.path.isdir(
            os.path.join(settings.MEDIA_ROOT, settings.SERIES_DIR, show)
        ):
            # Skip if not a directory
            continue
        # Iterate through seasons
        for _first in os.listdir(
            os.path.join(settings.MEDIA_ROOT, settings.SERIES_DIR, show)
        ):
            if os.path.isdir(
                os.path.join(settings.MEDIA_ROOT, settings.SERIES_DIR, show, _first)
            ):
                num_seasons += 1
                # Iterate through episodes
                for _second in os.listdir(
                    os.path.join(settings.MEDIA_ROOT, settings.SERIES_DIR, show, _first)
                ):
                    if os.path.isfile(
                        os.path.join(
                            settings.MEDIA_ROOT,
                            settings.SERIES_DIR,
                            show,
                            _first,
                            _second,
                        )
                    ) and is_video(_second):
                        num_files += 1

        # Only add show if it has at least one season
        if num_seasons > 0:
            shows.append(show)
            show_split = show.split(" ")

            if len(show_split) > 1:  # If show name has year
                name: str = " ".join(show_split[:-1])
                year = show_split[-1]
            else:
                name = show_split[0]
                year = "N/A"

            # Add show to table
            if show_index:
                table.add_row(
                    str(num_shows),
                    name,
                    year,
                    str(num_seasons),
                    str(num_files),
                )
            else:
                table.add_row(
                    name,
                    year,
                    str(num_seasons),
                    str(num_files),
                )

            num_shows += 1

    console.print(table)
    return shows, num_shows

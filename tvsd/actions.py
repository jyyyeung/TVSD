# -*- coding: utf-8 -*-
import logging
import os
import sys
from typing import List, Tuple
from tvsd._variables import BASE_PATH, TEMP_BASE_PATH, SERIES_DIR
from tvsd import state

from tvsd.download import Download
from tvsd.search import SearchQuery
from tvsd.utils import check_dir_mounted

from rich.console import Console
from rich.table import Table


def search_media_and_download(query: str):
    """Search for media and download

    Args:
        query (str): query string
    """
    logging.info(f"Checking if {BASE_PATH} is mounted...")
    if not check_dir_mounted(path=BASE_PATH):
        sys.exit()
    logging.debug("Base path: %s", BASE_PATH)

    # Search
    query_instance = SearchQuery(query)
    logging.info(f"Searching for {query}...")
    query_instance.find_show(BASE_PATH)

    # Download
    download_instance = Download(
        target=query_instance.chosen_show,
        base_path=BASE_PATH,
        temp_path=TEMP_BASE_PATH,
    )
    logging.info(f"Starting {query_instance.chosen_show.title} guided download...")
    download_instance.guided_download()


def list_shows_as_table(show_index=False) -> Tuple[List[str], int]:
    """List all shows in base directory as a table

    Args:
        show_index (bool, optional): Whether to print the row index as the first column, useful for selection. Defaults to False.

    Returns:
        Tuple[List[str], int]: List of shows and number of shows
    """
    console = Console()
    table = Table("Name", "Year", "#Seasons", "#Episodes")
    shows = []
    num_shows = 0
    if show_index:
        table = Table("#", "Name", "Year", "#Seasons", "#Episodes")

    for show in os.listdir(os.path.join(BASE_PATH, SERIES_DIR)):
        num_files = 0
        num_seasons = 0
        # Iterate through seasons
        for _first in os.listdir(os.path.join(BASE_PATH, SERIES_DIR, show)):
            if os.path.isdir(os.path.join(BASE_PATH, SERIES_DIR, show, _first)):
                num_seasons += 1
                # Iterate through episodes
                for _second in os.listdir(
                    os.path.join(BASE_PATH, SERIES_DIR, show, _first)
                ):
                    if os.path.isfile(
                        os.path.join(BASE_PATH, SERIES_DIR, show, _first, _second)
                    ) and _second.endswith(".mp4"):
                        num_files += 1

        # Only add show if it has at least one season
        if num_seasons > 0:
            shows.append(show)
            # Add show to table
            if show_index:
                table.add_row(
                    str(num_shows),
                    show.split(" ")[0],
                    show.split(" ")[1],
                    str(num_seasons),
                    str(num_files),
                )
            else:
                table.add_row(
                    show.split(" ")[0],
                    show.split(" ")[1],
                    str(num_seasons),
                    str(num_files),
                )

            num_shows += 1

    console.print(table)
    return shows, num_shows

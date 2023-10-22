# -*- coding: utf-8 -*-
import logging
import os
import sys
from typing import List, Tuple

from rich.console import Console
from rich.table import Table

from tvsd._variables import state_base_path, state_series_dir, state_temp_base_path
from tvsd.download import Download
from tvsd.search import SearchQuery
from tvsd.utils import check_dir_mounted, is_video


def search_media_and_download(query: str, specials_only: bool = False):
    """Search for media and download

    Args:
        query (str): query string
        specials_only (bool): Download only specials episode. Defaults to False.
    """
    logging.info("Checking if %s is mounted...", state_base_path())
    if not check_dir_mounted(path=state_base_path()):
        sys.exit()
    logging.debug("Base path: %s", state_base_path())

    # Search
    query_instance = SearchQuery(query)
    logging.info("Searching for %s...", query)
    query_instance.find_show(state_base_path())

    # Download
    download_instance = Download(
        target=query_instance.chosen_show,
        base_path=state_base_path(),
        temp_path=state_temp_base_path(),
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
    series_dir = os.path.join(state_base_path(), state_series_dir())
    logging.info("Checking if %s exists...", series_dir)
    if not os.path.isdir(series_dir):
        logging.error("%s does not exist! Nothing to list. Exiting...", series_dir)
        sys.exit()

    console = Console()
    table = Table("Name", "Year", "#Seasons", "#Episodes")
    shows = []
    num_shows = 0
    if show_index:
        table = Table("#", "Name", "Year", "#Seasons", "#Episodes")

    for show in os.listdir(os.path.join(state_base_path(), state_series_dir())):
        num_files = 0
        num_seasons = 0
        if not os.path.isdir(os.path.join(state_base_path(), state_series_dir(), show)):
            # Skip if not a directory
            continue
        # Iterate through seasons
        for _first in os.listdir(
            os.path.join(state_base_path(), state_series_dir(), show)
        ):
            if os.path.isdir(
                os.path.join(state_base_path(), state_series_dir(), show, _first)
            ):
                num_seasons += 1
                # Iterate through episodes
                for _second in os.listdir(
                    os.path.join(state_base_path(), state_series_dir(), show, _first)
                ):
                    if os.path.isfile(
                        os.path.join(
                            state_base_path(), state_series_dir(), show, _first, _second
                        )
                    ) and is_video(_second):
                        num_files += 1

        # Only add show if it has at least one season
        if num_seasons > 0:
            shows.append(show)
            show_split = show.split(" ")

            if len(show_split) > 1:  # If show name has year
                name = " ".join(show_split[:-1])
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

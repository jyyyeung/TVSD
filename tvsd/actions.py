# -*- coding: utf-8 -*-
import logging
import os
import sys
from typing import List, Tuple, TypedDict

import typer
from rich.console import Console
from rich.table import Table

from tvsd.types.season import Season

from .config import settings
from .download import Download
from .search import SearchQuery
from .utils import dir_exists, is_video


def search_media(query: str, sources: List[str] = []) -> List[Season]:
    """Search for media

    This function searches for media based on the given query string.

    Args:
        query (str): query string
        sources (List[str]): List of sources to search
        specials_only (bool): Download only specials episode. Defaults to False.

    Returns:
        List[Season]: A list of seasons
    """
    if not dir_exists(
        path=settings.MEDIA_ROOT, create_if_not=settings.CREATE_MEDIA_ROOT
    ):
        raise typer.Exit(code=1)

    logging.debug("Media Root: %s", settings.MEDIA_ROOT)

    query_instance = SearchQuery(query, sources=sources)

    if not dir_exists(path=settings.TEMP_ROOT, create_if_not=settings.CREATE_TEMP_ROOT):
        raise typer.Exit(code=1)

    logging.debug("Temp Root: %s", settings.TEMP_ROOT)

    logging.info("Searching for %s...", query)
    shows = query_instance.find_shows()

    return shows


def search_media_and_download(
    query: str, specials_only: bool = False, interactive: bool = True
) -> None | Season:
    """Search for media and download

    This function searches for media based on the given query string and downloads it.
    It first checks if the base path is mounted and exits if it is not.
    Then it searches for the given query and finds the show.
    Finally, it starts a guided download of the chosen show.

    Args:
        query (str): query string
        specials_only (bool): Download only specials episode. Defaults to False.
        interactive (bool): Whether to run in interactive mode. If False, the function will return a tuple of (ShowDict, int). Defaults to True.
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

    if interactive:
        download_instance.guided_download()
        return None
    else:
        # TODO: Continue here
        return query_instance.chosen_show


class DownloadOptions(TypedDict):
    specials_only: bool
    episodes: List[int]


def download_show(show: Season, options: DownloadOptions) -> None:
    """Download a show

    This function downloads a show.

    Args:
        show (Season): The show to download
    """
    download_instance = Download(
        target=show,
        specials_only=options.specials_only,
    )
    if options.episodes:
        download_instance.download_episodes(options.episodes)
    else:
        download_instance.download_all()


class ShowDict(TypedDict):
    name: str
    title: str
    year: str
    num_seasons: int
    index: int


def list_shows_as_table(show_index=False) -> Tuple[List[ShowDict], int]:
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

    for show_name in os.listdir(os.path.join(settings.MEDIA_ROOT, settings.SERIES_DIR)):
        num_files = 0
        num_seasons = 0
        if not os.path.isdir(
            os.path.join(settings.MEDIA_ROOT, settings.SERIES_DIR, show_name)
        ):
            # Skip if not a directory
            continue
        # Iterate through seasons
        for _first in os.listdir(
            os.path.join(settings.MEDIA_ROOT, settings.SERIES_DIR, show_name)
        ):
            if os.path.isdir(
                os.path.join(
                    settings.MEDIA_ROOT, settings.SERIES_DIR, show_name, _first
                )
            ):
                num_seasons += 1
                # Iterate through episodes
                for _second in os.listdir(
                    os.path.join(
                        settings.MEDIA_ROOT, settings.SERIES_DIR, show_name, _first
                    )
                ):
                    if os.path.isfile(
                        os.path.join(
                            settings.MEDIA_ROOT,
                            settings.SERIES_DIR,
                            show_name,
                            _first,
                            _second,
                        )
                    ) and is_video(_second):
                        num_files += 1

        # Only add show if it has at least one season
        if num_seasons > 0:
            # Split show name into name and year
            show_split = show_name.split(" ")

            if len(show_split) > 1:  # If show name has year
                name: str = " ".join(show_split[:-1])
                year = show_split[-1]
            else:
                name = show_split[0]
                year = "N/A"

            # Add show to list
            show = ShowDict(
                name=name,
                title=show_name,
                year=year.replace("(", "").replace(")", ""),
                num_seasons=num_seasons,
                index=num_shows,
            )
            shows.append(show)

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

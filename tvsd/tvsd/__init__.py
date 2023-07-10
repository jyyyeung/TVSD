# -*- coding: utf-8 -*-

import logging
import os

import typer
from dotenv import load_dotenv
from tvsd.download import Download
from tvsd.search import SearchQuery
from tvsd.utils import check_dir_mounted, LOGGER


load_dotenv()

app = typer.Typer()


temp_base_path = os.getenv("TEMP_PATH")  # TODO: Create if does not exist
base_path: str | None = os.getenv("DEST_PATH")

global db


# TODO: Database query for specials index for a particular episode
# TODO: Allow submit changes to database?


def search_media_and_download(query: str):
    """Search for media and download

    Args:
        query (str): query string
    """
    query_instance = SearchQuery(query)
    query_instance.find_show(base_path)
    download_instance = Download(
        target=query_instance.chosen_show,
        base_path=base_path,
        temp_path=temp_base_path,
    )
    download_instance.guided_download()


def quick_start():
    """Quick start"""

    # TODO: dynamic directory
    check_dir_mounted(base_path)
    LOGGER.debug("Base path: %s", base_path)
    typer.run(search_media_and_download)

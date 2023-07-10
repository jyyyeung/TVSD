# -*- coding: utf-8 -*-
import sys

from tvsd.download import Download
from tvsd.search import SearchQuery
from tvsd.utils import BASE_PATH, TEMP_BASE_PATH, check_dir_mounted, LOGGER


def search_media_and_download(query: str):
    """Search for media and download

    Args:
        query (str): query string
    """
    LOGGER.info(f"Checking if {BASE_PATH} is mounted...")
    if not check_dir_mounted(path=BASE_PATH):
        sys.exit()
    LOGGER.debug("Base path: %s", BASE_PATH)

    # Search
    query_instance = SearchQuery(query)
    LOGGER.info(f"Searching for {query}...")
    query_instance.find_show(BASE_PATH)

    # Download
    download_instance = Download(
        target=query_instance.chosen_show,
        base_path=BASE_PATH,
        temp_path=TEMP_BASE_PATH,
    )
    LOGGER.info(f"Starting {query_instance.chosen_show.title} guided download...")
    download_instance.guided_download()

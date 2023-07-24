# -*- coding: utf-8 -*-
import logging
import sys
from tvsd.config import BASE_PATH, TEMP_BASE_PATH

from tvsd.download import Download
from tvsd.search import SearchQuery
from tvsd.utils import check_dir_mounted


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

# -*- coding: utf-8 -*-
from typing import Any

from bs4 import BeautifulSoup, ResultSet, Tag

from tvsd.sources.base import Source


class Name(Source):
    """Name class"""

    def __init__(self):
        super().__init__()  # Call parent constructor

        ### Any variables you want to use below ###
        self.__status__ = "dev"

    ### SEARCHING FOR A SHOW ###

    def _search_url(self, search_query: str) -> str:
        # TODO: Set search url
        return None

    def _get_query_results(self, query_result_soup: BeautifulSoup) -> ResultSet[Any]:
        # TODO: Find all query results from soup
        return None

    ##### PARSE EPISODE DETAILS FROM URL #####

    def _set_relative_episode_url(self, soup: Tag) -> str:
        # TODO: Set relative episode url from soup
        return None

    def _set_season_title(self, soup: BeautifulSoup):
        # TODO: Set season title from soup
        return None

    ##### PARSE SEASON FROM QUERY RESULT #####

    def _get_result_note(self, query_result: BeautifulSoup) -> str:
        # TODO: Set result note from query result
        return None

    def _get_result_source_id(self, query_result: BeautifulSoup) -> str:
        # TODO: Set result source id from query result [Optional, for _get_result_details_url() use]
        return None

    def _get_result_details_url(self, query_result: BeautifulSoup) -> str:
        # TODO: Set result details url from query result
        return None

    #### PARSE SEASON DETAILS FROM DETAILS URL ####

    def _set_episode_title(self, soup: Tag) -> str:
        # TODO: Set episode title from soup
        return None

    def _set_season_description(self, soup: BeautifulSoup):
        # TODO: Set season description from soup
        return None

    def _set_season_episodes(self, soup: BeautifulSoup):
        # TODO: Set season episodes from soup
        return None

    def _set_season_year(self, soup: BeautifulSoup):
        # TODO: Set season year from soup
        return None

    ######## FETCH EPISODE M3U8 ########

    def _episode_url(self, relative_episode_url: str) -> str:
        # TODO: Set episode url from relative episode url
        return None

    def _set_episode_script(self, episode_soup: BeautifulSoup) -> str:
        # TODO: Set episode script from episode soup
        return None

    def _set_episode_m3u8(self, episode_script: str) -> str:
        # TODO: Set episode m3u8 from episode script
        return None

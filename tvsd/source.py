import json
import os
from typing import TYPE_CHECKING, Any, List, Union
from bs4 import BeautifulSoup, ResultSet

import cloudscraper

from tvsd.show import Show

if TYPE_CHECKING:
    from tvsd.season import Season
    from tvsd.custom_types import EpisodeDetailsFromURL, SeasonDetailsFromURL


def load_source_details(season_dir: str):
    """Loads the source details from the season directory

    Args:
        season_dir (str): Season directory

    Returns:
        Any: source details
    """
    # print(season_dir)
    dir_file = os.path.join(season_dir, "YYYDown_show.json")
    if not os.path.isfile(dir_file):
        return None
    show_details = json.load(open(dir_file, "r"))
    # print(show_details)
    source = Source(show_details["source"])

    # TODO: Complete this

    # if source == Source.XiaoBao:
    #     return XiaoBao.from_json(show_details)
    # if source == Source.MOV:
    #     return MOV.from_json(show_details)
    # if source == Source.YingHua:
    #     return YingHua.from_json(show_details)
    # if source == Source.OLEVOD:
    #     return OLEVOD.from_json(show_details)


class Source:
    """Source class"""

    def __init__(self) -> None:
        self._scraper = cloudscraper.create_scraper(
            delay=10,
            browser={
                "custom": "ScraperBot/1.0",
            },
        )
        self._query: str
        self._results: List[Season]
        self._exists_locally: bool
        self._chosen_show: Season

        self._search_url: str = None
        self._search_result_page: str = None
        self._query_result_soup: BeautifulSoup = None
        self._result_list: Union[Show, Season] = []
        self._result_index: int = 1
        self._query_results: ResultSet[Any] = None

    @classmethod
    def fetch_details_soup(cls, details_url: str) -> BeautifulSoup:
        """Grabs the details page soup

        Returns:
            BeautifulSoup: Soup of details page
        """
        scraper = cloudscraper.create_scraper(
            delay=10,
            browser={
                "custom": "ScraperBot/1.0",
            },
        )
        show_details_page = scraper.get(details_url).content
        soup: BeautifulSoup = BeautifulSoup(show_details_page, "html.parser")
        return soup

    @classmethod
    def query_from_source(cls, query: str):
        """Queries the source for the query

        Args:
            query (str): Query to search for
        """
        pass

    @classmethod
    def parse_episode_details_from_li(
        cls, soup: BeautifulSoup
    ) -> "EpisodeDetailsFromURL":
        """Parses the episode details from the soup

        Args:
            soup (BeautifulSoup): Soup of the episode details page

        Returns:
            Episode: Episode object
        """
        pass

    @classmethod
    def parse_from_json(cls, json_content):
        return cls(json_content)

    @classmethod
    def parse_from_query(cls, query_result: BeautifulSoup) -> "Season":
        """Parses the query result

        Args:
            query_result (BeautifulSoup): Query result

        Returns:
            Season: Season object
        """
        pass

    @classmethod
    def parse_season_from_details_url(cls, season_url: str) -> "SeasonDetailsFromURL":
        """Parses details from details url

        Args:
            details_url (str, optional): Details url to the result page. Defaults to None.

        Returns:
            dict: Details found on the details page
        """
        print("Method for finding details from this source is undefined...")
        return {}

    def fetch_episode_m3u8(self, episode_url: str) -> str:
        """Fetches the m3u8 url for the episode

        Args:
            episode_url (str): Episode url

        Returns:
            str | None: m3u8 url
        """
        print("Method for finding episode m3u8 from this source is undefined...")

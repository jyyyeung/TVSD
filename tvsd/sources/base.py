"""Base file for Sources"""
import errno
import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, List

import chinese_converter
from bs4 import BeautifulSoup, ResultSet, Tag

from tvsd.types import EpisodeDetailsFromURL, SeasonDetailsFromURL
from tvsd.types.season import Season
from tvsd.utils import SCRAPER


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


class Source(ABC):
    """Source class"""

    def __init__(self) -> None:
        self._query: str
        self._results: List[Season]
        self._exists_locally: bool
        self._chosen_show: Season

        self._query_result_soup: BeautifulSoup
        self._result_list: List[Season] = []
        self._query_results: ResultSet[Any]

        self.__status__ = "parent"

        self._domains: List[str] = []
        self._domain_index: int = 0

        self._is_simplified: bool = False
        self._is_traditional: bool = False

    # @classmethod
    # def parse_from_json(cls, json_content):
    #     return cls(json_content)

    ### SEARCHING FOR A SHOW ###

    def query_from_source(self, search_query: str) -> List[Season]:
        """
        query_from_source Searches for a show

        Args:
            search_query (str): Query to search for

        Returns:
            List[Season]: List of shows
        """
        if self._is_simplified:
            search_query = chinese_converter.to_simplified(search_query)
        if self._is_traditional:
            search_query = chinese_converter.to_traditional(search_query)

        search_url = self._search_url(search_query)

        logging.info("Searching %s...", {search_query})
        logging.debug("Searching for %s in %s", search_query, search_url)

        query_result_soup = self.get_query_result_soup(search_url)
        if query_result_soup is not None:
            query_results = self._get_query_results(query_result_soup)
            # Below are same for all
            self._result_list: List[Season] = []

            for result in query_results:
                show = self.parse_from_query(result)
                if show is not None:
                    self._result_list.append(show)

        if len(self._result_list) == 0 and len(self._domains) > self._domain_index + 1:
            self._domain_index += 1
            return self.query_from_source(search_query)

        return self._result_list

    @abstractmethod
    def _search_url(self, search_query: str) -> str:
        """Returns the search url for where to search for the query

        Args:
            query (str): Query to search for

        Returns:
            str: Search url
        """
        raise NotImplementedError

    @abstractmethod
    def _get_query_results(self, query_result_soup: BeautifulSoup) -> ResultSet[Any]:
        """Returns the query results from the soup

        Args:
            query_result_soup (BeautifulSoup): Soup of the query result

        Returns:
            ResultSet[Any]: Query results
        """
        raise NotImplementedError

    def get_query_result_soup(self, search_url: str) -> BeautifulSoup | None:
        """Returns the query result soup

        Args:
            search_url (str): Search url

        Returns:
            BeautifulSoup: Query result soup
        """
        try:
            search_result_page = SCRAPER.get(search_url).content
            query_result_soup: BeautifulSoup = BeautifulSoup(
                search_result_page, "html.parser"
            )
            return query_result_soup
        except ConnectionResetError as error:
            if error.errno != errno.ECONNRESET:
                raise  # Not error we are looking for
            logging.error("Connection reset by peer")
        except Exception as error:
            logging.error("Error in getting query result soup %s", error)
        return None

    ##### PARSE EPISODE DETAILS FROM URL #####

    def parse_episode_details_from_li(self, soup: Tag) -> "EpisodeDetailsFromURL":
        """Parses the episode details from the soup

        Args:
            soup (BeautifulSoup): Soup of the episode details page

        Returns:
            Episode: Episode object
        """

        episode_details: EpisodeDetailsFromURL = {
            "title": chinese_converter.to_simplified(self._set_episode_title(soup)),
            "url": self._set_relative_episode_url(soup),
        }
        return EpisodeDetailsFromURL(episode_details)

    @abstractmethod
    def _set_episode_title(self, soup: Tag) -> str:
        """Sets the episode title

        Args:
            soup (Tag): Soup of the episode details page

        Returns:
            str: Episode title
        """
        raise NotImplementedError

    @abstractmethod
    def _set_relative_episode_url(self, soup: Tag) -> str:
        """Sets the relative episode url

        Args:
            soup (Tag): Soup of the episode details page

        Returns:
            str: Relative episode url
        """
        raise NotImplementedError

    ##### PARSE SEASON FROM QUERY RESULT #####

    def parse_from_query(self, query_result: BeautifulSoup) -> "Season | None":
        """Parses the query result

        Args:
            query_result (BeautifulSoup): Query result

        Returns:
            Season: Season object
        """

        details_url = self._get_result_details_url(query_result)
        if details_url is None:
            return None

        note = self._get_result_note(query_result)
        details: "SeasonDetailsFromURL" = self.parse_season_from_details_url(
            details_url
        )
        if details is None:
            return None
        season = Season(
            note=note,
            details=details,
            details_url=details_url,
            fetch_episode_m3u8=self.fetch_episode_m3u8,
            episodes=details["episodes"],
            source=self,
        )
        return season

    @abstractmethod
    def _get_result_note(self, query_result: BeautifulSoup) -> str:
        """Gets the result note

        Args:
            query_result (BeautifulSoup): Query result

        Returns:
            str: Result note
        """
        raise NotImplementedError

    # @abstractmethod
    def _get_result_source_id(self, query_result: BeautifulSoup) -> str:
        """Gets the result source id

        Args:
            query_result (BeautifulSoup): Query result

        Returns:
            str: Result source id
        """
        raise NotImplementedError

    @abstractmethod
    def _get_result_details_url(self, query_result: BeautifulSoup) -> str:
        """Gets the result details url

        Args:
            source_id (str): Result source id

        Returns:
            str: Result details url
        """
        raise NotImplementedError

    #### PARSE SEASON DETAILS FROM DETAILS URL ####

    def parse_season_from_details_url(
        self, season_url: str
    ) -> "SeasonDetailsFromURL | None":
        """Parses details from details url

        Args:
            details_url (str, optional): Details url to the result page. Defaults to None.

        Returns:
            dict: Details found on the details page
        """
        soup = self.fetch_details_soup(season_url)
        if soup is None:
            return None
        details: SeasonDetailsFromURL = {
            "title": chinese_converter.to_simplified(self._set_season_title(soup)),
            "description": self._set_season_description(soup),
            "episodes": self._set_season_episodes(soup),
            "year": self._set_season_year(soup),
        }

        # print("Method for finding details from this source is undefined...")
        return SeasonDetailsFromURL(details)

    def fetch_details_soup(self, details_url: str) -> BeautifulSoup | None:
        """Grabs the details page soup

        Returns:
            BeautifulSoup: Soup of details page
        """

        try:
            show_details_page = SCRAPER.get(details_url).content
            soup: BeautifulSoup = BeautifulSoup(show_details_page, "html.parser")
            return soup
        except ConnectionResetError as error:
            if error.errno != errno.ECONNRESET:
                raise  # Not error we are looking for
            logging.error("Connection reset by peer")
        except Exception as error:
            logging.error("Error in getting season details soup: %s", error)
        return None

    @abstractmethod
    def _set_season_title(self, soup: BeautifulSoup) -> str:
        """Sets the season title

        Args:
            soup (BeautifulSoup): Soup of the season details page

        Returns:
            str: Season title
        """
        raise NotImplementedError

    @abstractmethod
    def _set_season_description(self, soup: BeautifulSoup) -> str:
        """Sets the season description

        Args:
            soup (BeautifulSoup): Soup of the season details page

        Returns:
            str: Season description
        """
        raise NotImplementedError

    @abstractmethod
    def _set_season_episodes(self, soup: BeautifulSoup) -> List[str]:
        """Sets the season episodes

        Args:
            soup (BeautifulSoup): Soup of the season details page

        Returns:
            List[str]: Season episodes
        """
        raise NotImplementedError

    @abstractmethod
    def _set_season_year(self, soup: BeautifulSoup) -> str:
        """Sets the season year

        Args:
            soup (BeautifulSoup): Soup of the season details page

        Returns:
            str: Season year
        """
        raise NotImplementedError

    ######## FETCH EPISODE M3U8 ########

    def fetch_episode_m3u8(self, relative_episode_url: str) -> str | None:
        """Fetches the m3u8 url for the episode

        Args:
            episode_url (str): Episode url

        Returns:
            str | None: m3u8 url
        """
        try:
            episode_url = self._episode_url(relative_episode_url)
            episode_details_page = SCRAPER.get(episode_url).content
            episode_soup: BeautifulSoup = BeautifulSoup(
                episode_details_page, "html.parser"
            )
            episode_script = self._set_episode_script(episode_soup)
            episode_m3u8 = self._set_episode_m3u8(episode_script)
            return episode_m3u8
        except ConnectionResetError as error:
            if error.errno != errno.ECONNRESET:
                raise  # Not error we are looking for
            logging.error("Connection reset by peer")
        except Exception as error:
            logging.error("Error in getting episode details soup: %s", error)
        return None

    @abstractmethod
    def _episode_url(self, relative_episode_url: str) -> str:
        """Returns the episode url

        Args:
            relative_episode_url (str): Relative episode url

        Returns:
            str: Episode url
        """
        return relative_episode_url

    @abstractmethod
    def _set_episode_script(self, episode_soup: BeautifulSoup) -> str:
        """Sets the episode script

        Args:
            episode_soup (BeautifulSoup): Soup of the episode details page

        Returns:
            str: Episode script
        """
        raise NotImplementedError

    @abstractmethod
    def _set_episode_m3u8(self, episode_script: str) -> str:
        """Sets the episode m3u8

        Args:
            episode_script (str): Episode script

        Returns:
            str: Episode m3u8
        """
        raise NotImplementedError

    ################

    @property
    def source_name(self) -> str:
        """Returns the name of the class

        Returns:
            str: Name of the class
        """
        return self.__class__.__name__

    @property
    def _domain(self):
        return self._domains[self._domain_index]

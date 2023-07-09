import logging
import re
from typing import TYPE_CHECKING, Any, List, Union
from typing_extensions import Literal

from bs4 import BeautifulSoup, ResultSet, Tag
from tvsd import utils
from tvsd.source import Source
from tvsd.custom_types import EpisodeDetailsFromURL, SeasonDetailsFromURL
from tvsd.season import Season

if TYPE_CHECKING:
    from tvsd.show import Show


class XiaoBao(Source):
    """XiaoBao class"""

    def query(
        self, search_query: str
    ) -> List[Union[Literal["Show"], Literal["Season"]]]:
        """Searches for a show

        Returns:
            Union(List[Show, Season], []): List of shows or seasons
        """
        self._search_url: str = (
            f"https://xiaoheimi.net/index.php/vod/search.html?wd={search_query}&submit="
        )
        scraper = self._scraper
        self._search_result_page = scraper.get(self._search_url).content

        self._query_result_soup: BeautifulSoup = BeautifulSoup(
            self._search_result_page, "html.parser"
        )

        self._query_results: ResultSet[Any] = self._query_result_soup.find_all(
            "li", attrs={"class": "clearfix"}
        )
        self._result_list: Union([Show, Season], []) = []
        self._result_index: int = 1

        for result in self._query_results:
            show = self.parse_from_query(result)
            self._result_list.append(show)
        return self._result_list

    # @classmethod
    # def from_json(cls, json_content):
    #     return cls(json_content)

    @classmethod
    def parse_from_query(cls, query_result: BeautifulSoup) -> "Season":
        page = query_result.find("a", attrs={"class": "myui-vodlist__thumb"})["href"]
        source_id = re.search(r"/index.php/vod/detail/id/(\d+).html", page).group(1)
        logging.info(source_id)
        note = query_result.find(
            "span", attrs={"class": "pic-text text-right"}
        ).get_text()
        details_url: str = (
            f"https://xiaoheimi.net/index.php/vod/detail/id/{source_id}.html"
        )
        details: "SeasonDetailsFromURL" = cls.parse_season_from_details_url(details_url)

        season = Season(
            note=note,
            details=details,
            details_url=details_url,
            fetch_episode_m3u8=cls.fetch_episode_m3u8,
            episodes=details["episodes"],
            source=cls,
        )

        return season

    @classmethod
    def parse_episode_details_from_li(cls, soup: Tag) -> "EpisodeDetailsFromURL":
        """Parses the episode details from the soup

        Args:
            soup (BeautifulSoup): Soup of the episode details page

        Returns:
            Episode: Episode object
        """

        episode_title = soup.find("a").get_text()
        logging.info(episode_title)
        episode_url = soup.find("a", attrs={"class": "btn btn-default"})["href"]

        episode_details = {
            "title": episode_title,
            "url": episode_url,
        }
        return episode_details

    @classmethod
    def parse_season_from_details_url(cls, season_url: str) -> "SeasonDetailsFromURL":
        """Parses the details page for the show

        Args:
            details_url (str): Details url to the result page

        Returns:
            dict: Details found on the details page
        """
        soup = super().fetch_details_soup(season_url)

        title = str(soup.title.string).replace(" - 小宝影院 - 在线视频", "") or None
        logging.info(title)
        description = (
            soup.find(
                "span", attrs={"class": "data", "style": "display: none;"}
            ).get_text()
            or None
        )
        logging.info(description)
        episodes = (
            soup.find("ul", attrs={"class": "myui-content__list"}).contents or None
        )
        logging.info(episodes)
        year = (
            str(soup.find("p", attrs={"class": "data"}).contents[-1].get_text()) or None
        )
        logging.info(year)

        details = {
            "title": title,
            "description": description,
            "episodes": episodes,
            "year": year,
        }

        return SeasonDetailsFromURL(details)

    @classmethod
    def fetch_episode_m3u8(cls, episode_url: str) -> str:
        """Fetches the m3u8 url for the episode

        Args:
            episode_url (str): Episode url

        Returns:
            str: m3u8 url
        """
        episode_details_page = utils.SCRAPER.get(
            f"https://xiaoheimi.net{episode_url}"
        ).content
        episode_soup: BeautifulSoup = BeautifulSoup(episode_details_page, "html.parser")
        episode_script: str = str(
            episode_soup.find("div", attrs={"class": "myui-player__box"}).find("script")
        )
        episode_m3u8_format = (
            r"https:\\\/\\\/m3u.haiwaikan.com\\\/xm3u8\\\/[\w\d]+.m3u8"
        )

        episode_m3u8 = re.findall(episode_m3u8_format, episode_script)[0].replace(
            "\\", ""
        )
        return episode_m3u8

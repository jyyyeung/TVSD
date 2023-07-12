import re
from typing import Any

from bs4 import BeautifulSoup, ResultSet, Tag

from tvsd.source import Source


class SSSTV(Source):
    """777tv class"""

    source_url = "https://777tv.tw"

    def __init__(self):
        super().__init__()
        self.__status__ = "active"

    ### SEARCHING FOR A SHOW ###

    def _search_url(self, search_query: str) -> str:
        return f"{self.source_url}/vodsearch/-------------.html?wd={search_query}"

    def _get_query_results(self, query_result_soup: BeautifulSoup) -> ResultSet[Any]:
        return query_result_soup.find_all("div", attrs={"class": "module-search-item"})

    ##### PARSE EPISODE DETAILS FROM URL #####

    def _set_relative_episode_url(self, soup: Tag) -> str:
        return soup["href"]

    def _set_episode_title(self, soup: Tag) -> str:
        return soup.find("span").get_text()

    ##### PARSE SEASON FROM QUERY RESULT #####

    def _get_result_note(self, query_result: BeautifulSoup) -> str:
        note = query_result.find("a", attrs={"class": "video-serial"}).get_text()
        return note

    def _get_result_details_url(self, query_result: BeautifulSoup) -> str:
        relative_url = query_result.find("a", attrs={"class": "video-serial"})["href"]

        return f"{self.source_url}{relative_url}"

    #### PARSE SEASON DETAILS FROM DETAILS URL ####

    def _set_season_title(self, soup: BeautifulSoup):
        return soup.find("h1", attrs={"class": "page-title"}).get_text()

    def _set_season_description(self, soup: BeautifulSoup):
        return (
            soup.find("div", attrs={"class": "video-info-content"})
            .find("span")
            .get_text()
        )

    def _set_season_episodes(self, soup: BeautifulSoup):
        return (
            soup.find("div", attrs={"class": "module-player-list"})
            .find("div", attrs={"class": "scroll-content"})
            .find_all("a")
        )

    def _set_season_year(self, soup: BeautifulSoup):
        return soup.find(
            "a",
            {
                "class": "tag-link",
                "href": re.compile(r"/vodshow/\d{2}-+\d{4}.html"),
            },
        ).get_text()

    ######## FETCH EPISODE M3U8 ########

    def _episode_url(self, relative_episode_url: str) -> str:
        return self.source_url + relative_episode_url

    def _set_episode_script(self, episode_soup: BeautifulSoup) -> str:
        return str(
            episode_soup.find("div", attrs={"class": "player-wrapper"}).find("script")
        )

    def _set_episode_m3u8(self, episode_script: str) -> str:
        print(episode_script)
        return (
            re.findall(
                r"\"url\":\"https:[\w\d\-\_\\\/\.]*\.m3u8\"",
                episode_script,
            )[0]
            .replace("\\", "")
            .replace('"url":', "")
            .replace('"', "")
        )

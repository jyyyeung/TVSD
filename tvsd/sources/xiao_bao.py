import re
from typing import Any

from bs4 import BeautifulSoup, ResultSet, Tag

from tvsd.sources.base import Source


class XiaoBao(Source):
    """XiaoBao class"""

    def __init__(self):
        super().__init__()  # Call parent constructor
        self.__status__ = "active"
        self._domains = ["https://xiaoheimi.net"]
        self._is_simplified = True

    ### SEARCHING FOR A SHOW ###

    def _search_url(self, search_query: str) -> str:
        return f"{self._domain}/index.php/vod/search.html?wd={search_query}&submit="

    def _get_query_results(self, query_result_soup: BeautifulSoup) -> ResultSet[Any]:
        return query_result_soup.find_all("li", attrs={"class": "clearfix"})

    ##### PARSE EPISODE DETAILS FROM URL #####

    def _set_episode_title(self, soup: Tag) -> str:
        return soup.find("a").get_text()

    def _set_relative_episode_url(self, soup: Tag) -> str:
        return soup.find("a")["href"]

    ##### PARSE SEASON FROM QUERY RESULT #####

    def _get_result_note(self, query_result: BeautifulSoup) -> str:
        note = query_result.find(
            "span", attrs={"class": "pic-text text-right"}
        ).get_text()
        return note

    def _get_result_source_id(self, query_result: BeautifulSoup) -> str:
        page = query_result.find("a", attrs={"class": "myui-vodlist__thumb"})["href"]
        source_id = re.search(r"/index.php/vod/detail/id/(\d+).html", page).group(1)
        return source_id

    def _get_result_details_url(self, query_result: BeautifulSoup) -> str:
        source_id = self._get_result_source_id(query_result=query_result)
        return f"{self._domain}/index.php/vod/detail/id/{source_id}.html"

    #### PARSE SEASON DETAILS FROM DETAILS URL ####

    def _set_season_title(self, soup: BeautifulSoup) -> str:
        return str(soup.title.string).replace(" - 小宝影院 - 在线视频", "") or None

    def _set_season_description(self, soup: BeautifulSoup):
        return soup.find(
            "span", attrs={"class": "data", "style": "display: none;"}
        ).get_text()

    def _set_season_episodes(self, soup: BeautifulSoup):
        return soup.find("ul", attrs={"class": "myui-content__list"}).contents or None

    def _set_season_year(self, soup: BeautifulSoup):
        return (
            str(soup.find("p", attrs={"class": "data"}).contents[-1].get_text()) or None
        )

    ######## FETCH EPISODE M3U8 ########

    def _episode_url(self, relative_episode_url: str) -> str:
        return f"{self._domain}{relative_episode_url}"

    def _set_episode_script(self, episode_soup: BeautifulSoup) -> str:
        return str(
            episode_soup.find("div", attrs={"class": "myui-player__box"}).find("script")
        )

    def _set_episode_m3u8(self, episode_script: str) -> str:
        episode_m3u8_format = (
            r"https:\\\/\\\/m3u.haiwaikan.com\\\/xm3u8\\\/[\w\d]+.m3u8"
        )

        episode_m3u8 = re.findall(episode_m3u8_format, episode_script)[0].replace(
            "\\", ""
        )
        return episode_m3u8

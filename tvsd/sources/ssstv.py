import re
from typing import Any

from bs4 import BeautifulSoup, ResultSet, Tag

from tvsd.sources.base import Source


class SSSTV(Source):
    """777tv class"""

    def __init__(self):
        super().__init__()
        self.__status__ = "active"
        self._domains = ["https://777tv.tw"]

    ### SEARCHING FOR A SHOW ###

    def _search_url(self, search_query: str) -> str:
        return f"{self._domain}/vodsearch/-------------.html?wd={search_query}"

    def _get_query_results(self, query_result_soup: BeautifulSoup) -> ResultSet[Any]:
        return query_result_soup.find_all("div", attrs={"class": "module-search-item"})

    ##### PARSE EPISODE DETAILS FROM URL #####

    def _set_relative_episode_url(self, soup: Tag) -> str:
        return soup["href"]

    def _set_episode_title(self, soup: Tag) -> str:
        span_tag = soup.find("span")
        if span_tag:
            return span_tag.get_text()
        return ""

    ##### PARSE SEASON FROM QUERY RESULT #####

    def _get_result_note(self, query_result: BeautifulSoup) -> str:
        note_tag = query_result.find("a", attrs={"class": "video-serial"})
        if note_tag:
            return note_tag.get_text()
        return ""

    def _get_result_details_url(self, query_result: BeautifulSoup) -> str:
        relative_url_tag = query_result.find("a", attrs={"class": "video-serial"})
        if relative_url_tag:
            relative_url = relative_url_tag["href"]
            return f"{self._domain}{relative_url}"
        return ""

    #### PARSE SEASON DETAILS FROM DETAILS URL ####

    def _set_season_title(self, soup: BeautifulSoup):
        title_tag = soup.find("h1", attrs={"class": "page-title"})
        if title_tag:
            return title_tag.get_text()
        return ""

    def _set_season_description(self, soup: BeautifulSoup):
        description_tag = soup.find("div", attrs={"class": "video-info-content"})
        if description_tag:
            span_tag = description_tag.find("span")
            if span_tag is not None:
                return span_tag.text
        return ""

    def _set_season_episodes(self, soup: BeautifulSoup):
        module_player_list = soup.find("div", class_="module-player-list")
        if module_player_list:
            scroll_content = module_player_list.find(
                "div", attrs={"class": "scroll-content"}
            )
            if scroll_content:
                return scroll_content.find_all("a", recursive=False)
        return []

    def _set_season_year(self, soup: BeautifulSoup):
        year_tag = soup.find(
            "a",
            href=re.compile(r"/vodshow/\d+-+\d{4}.html"),
        )
        if year_tag:
            return year_tag.get_text()
        return ""

    ######## FETCH EPISODE M3U8 ########

    def _episode_url(self, relative_episode_url: str) -> str:
        return self._domain + relative_episode_url

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

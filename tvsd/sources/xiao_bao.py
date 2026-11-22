import json
import logging
import re
from typing import Any

from bs4 import BeautifulSoup, ResultSet, Tag

from tvsd.sources.base import Source

# The site appends its own branding, status and promo tokens to <title>, e.g.
# "庆余年第二季(2024) 已完结 免费在线观看 - 小宝影院". Plex names must not carry them.
# "第N季" is kept (season detection in Season.determine_season_index needs it) but is
# turned into a separate word, because Show.generate_show_prefix drops everything from
# " 第" onwards.
_SITE_SUFFIX_REGEX = re.compile(
    r"\s*[-–—]\s*(?:小宝影院|小宝影视|在线视频|ibaotv|xiaoheimi).*$", re.IGNORECASE
)
_TITLE_NOISE_TOKENS = (
    "免费在线观看",
    "高清完整版",
    "在线观看",
    "已完结",
    "已完結",
    "全集",
    "高清",
    "HD",
)
_UPDATE_TO_REGEX = re.compile(r"更新至\s*\d+\s*[集期].*$")
_YEAR_SUFFIX_REGEX = re.compile(r"\s*[(（]\d{4}[)）]\s*$")
_SEASON_TOKEN_REGEX = re.compile(r"(?<=[^\s])(第[一二三四五六七八九十]+季)")
_YEAR_REGEX = re.compile(r"\d{4}")


def _clean_season_title(raw_title: str) -> str:
    """Strip site branding, promo/status tokens and the year suffix from a page title.

    Args:
        raw_title (str): The raw ``<title>`` of a details page.

    Returns:
        str: The cleaned show title, e.g. ``庆余年 第二季``.
    """
    title = _SITE_SUFFIX_REGEX.sub("", raw_title)
    title = _UPDATE_TO_REGEX.sub("", title)
    for token in _TITLE_NOISE_TOKENS:
        title = title.replace(token, " ")
    title = _YEAR_SUFFIX_REGEX.sub("", title)
    title = _SEASON_TOKEN_REGEX.sub(r" \1", title)
    title = re.sub(r"\s{2,}", " ", title).strip()
    return title

class XiaoBao(Source):
    """XiaoBao class"""

    def __init__(self) -> None:
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
        return _clean_season_title(str(soup.title.string)) or None

    def _set_season_description(self, soup: BeautifulSoup):
        return soup.find(
            "span", attrs={"class": "data", "style": "display: none;"}
        ).get_text()

    def _set_season_episodes(self, soup: BeautifulSoup):
        return soup.find("ul", attrs={"class": "myui-content__list"}).contents or None

    def _set_season_year(self, soup: BeautifulSoup):
        data = str(soup.find("p", attrs={"class": "data"}).contents[-1].get_text())
        year = _YEAR_REGEX.search(data)
        return year.group(0) if year else None

    ######## FETCH EPISODE M3U8 ########

    def _episode_url(self, relative_episode_url: str) -> str:
        return f"{self._domain}{relative_episode_url}"

    def _set_episode_script(self, episode_soup: BeautifulSoup) -> str:
        return str(
            episode_soup.find("div", attrs={"class": "myui-player__box"}).find("script")
        )

    def _set_episode_m3u8(self, episode_script: str) -> str:
        logging.debug(episode_script)

        episode_m3u8_format = (
            r"https:\\\/\\\/[\w\d\.\\\/]+\.m3u8"
        )

        episode_m3u8 = re.findall(episode_m3u8_format, episode_script)[0].replace(
            "\\", ""
        )

        logging.debug(episode_m3u8)
        return episode_m3u8
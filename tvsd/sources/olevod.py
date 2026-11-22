import errno
import logging
import re
import time
from typing import Any

from bs4 import BeautifulSoup, ResultSet, Tag

from tvsd.sources.base import Source
from tvsd.utils import SCRAPER


class OLEVOD(Source):
    """Olevod class"""

    def __init__(self) -> None:
        super().__init__()  # Call parent constructor
        # DEAD as of 2026-11: the site serves a Vue SPA (WASM player, encrypted
        # requests) instead of server-rendered HTML, so the scraping selectors no
        # longer match anything. Kept as a starting point, not queried.
        self.__status__ = "dead"
        # self._domains = ["https://olevod.com", "https://olevod1.com"]
        self._domains = ["https://olevod.com"]
        self._is_simplified = True

    ### SEARCHING FOR A SHOW ###

    def _search_url(self, search_query: str) -> str:
        return f"{self._domain}/index.php/vod/search.html?wd={search_query}&submit="

    def _get_query_results(self, query_result_soup: BeautifulSoup) -> ResultSet[Any]:
        # TODO: Auto JS Guard
        logging.debug(query_result_soup)
        # query_result = []
        # query_result += query_result_soup.find_all(
        #     "li", attrs={"class": "searchlist_item"}
        # )
        # query_result += query_result_soup.find_all(
        #     "li", attrs={"class": "hl-list-item"}
        # )
        # return query_result
        return query_result_soup.find_all("li", attrs={"class": "searchlist_item"})

    ##### PARSE EPISODE DETAILS FROM URL #####

    def _set_relative_episode_url(self, soup: Tag) -> str:
        a_tag = soup.find("a")
        if a_tag is None:
            logging.error("No a tag found")
            return ""
        href = a_tag.get("href", "")
        return str(href) if href else ""

    def _set_season_title(self, soup: BeautifulSoup) -> str:
        title = soup.find("h2", attrs={"class": "title"})
        if title:
            return title.get_text(strip=True)
        return ""

    ##### PARSE SEASON FROM QUERY RESULT #####

    def _get_result_note(self, query_result: BeautifulSoup) -> str:
        try:
            note = query_result.find("span", attrs={"class": "pic_text text_right"})
            if note:
                return note.get_text(strip=True)
        except AttributeError:
            pass
        return ""

    def _get_result_source_id(self, query_result: BeautifulSoup) -> str:
        page_tag = query_result.find("a", attrs={"class": "vodlist_thumb"})
        if page_tag is None:
            logging.error("Cannot Find Page Tag in query result")
            return ""
        page = page_tag["href"]
        match = re.search(r"/index.php/vod/detail/id/(\d+).html", str(page))
        if match is None:
            logging.error("Cannot Find Source ID in query result")
            return ""
        return match.group(1)

    def _get_result_details_url(self, query_result: BeautifulSoup) -> str:
        source_id = self._get_result_source_id(query_result=query_result)

        return f"https://www.olevod.com/index.php/vod/detail/id/{source_id}.html"

    #### PARSE SEASON DETAILS FROM DETAILS URL ####

    def _set_episode_title(self, soup: Tag) -> str:
        title_tag = soup.find("a")
        if title_tag is None:
            logging.error("Cannot Find Title Tag in episode details page")
            return ""
        return title_tag.get_text(strip=True)

    def _set_season_description(self, soup: BeautifulSoup):
        logging.debug(soup.find("div", attrs={"class": "content_desc"}))

        desc_wrap = soup.find("div", attrs={"class": "content_desc"})
        if desc_wrap is None:
            logging.error("Cannot Find Description Wrap in episode details page")
            return ""
        span = desc_wrap.find("span")
        if span is None:
            logging.error(
                "Cannot Find Span in Description Wrap in episode details page"
            )
            return ""
        return span.get_text(strip=True)

    def _set_season_episodes(self, soup: BeautifulSoup):
        episodes_list = soup.find("ul", attrs={"class": "content_playlist"})
        if episodes_list is None:
            logging.error("Cannot Find Episodes List in episode details page")
            return []
        return episodes_list.find_all("li")

    def _set_season_year(self, soup: BeautifulSoup):
        year_tag = soup.find(
            "a", {"href": re.compile(r"/index.php/vod/search/year/[0-9]{4}.html")}
        )
        if year_tag is None:
            logging.error("Cannot Find Year Tag in episode details page")
            return ""
        return year_tag.get_text(strip=True) or ""

    ######## FETCH EPISODE M3U8 ########

    def _episode_url(self, relative_episode_url: str) -> str:
        return "https://www.olevod.com" + relative_episode_url

    def _set_episode_script(self, episode_soup: BeautifulSoup) -> str:
        video_div = episode_soup.find("div", attrs={"class": "player_video"})
        if video_div is None:
            logging.error("Cannot Find Video Div in episode details page")
            return ""
        script_tag = video_div.find("script")
        if script_tag is None:
            logging.error("Cannot Find Script Tag in episode details page")
            return ""
        return str(script_tag)

    def _set_episode_m3u8(self, episode_script: str) -> str:
        return re.findall(
            r"https:\\\/\\\/europe.olemovienews.com[\w\d\/\\\.]*.m3u8", episode_script
        )[0].replace("\\", "")

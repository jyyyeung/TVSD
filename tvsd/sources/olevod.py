import logging
import re
from typing import Any

from bs4 import BeautifulSoup, ResultSet, Tag

from tvsd.sources.base import Source


class OLEVOD(Source):
    """Olevod class"""

    def __init__(self):
        super().__init__()  # Call parent constructor
        self.__status__ = "active"
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
        return soup.find("a").get("href", "")

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
        page = query_result.find("a", attrs={"class": "vodlist_thumb"})["href"]
        return re.search(r"/index.php/vod/detail/id/(\d+).html", page).group(1)

    def _get_result_details_url(self, query_result: BeautifulSoup) -> str:
        source_id = self._get_result_source_id(query_result=query_result)

        return f"https://www.olevod.com/index.php/vod/detail/id/{source_id}.html"

    #### PARSE SEASON DETAILS FROM DETAILS URL ####

    def _set_episode_title(self, soup: Tag) -> str:
        return soup.find("a").get_text()

    def _set_season_description(self, soup: BeautifulSoup):
        return soup.find("div", attrs={"class": "content_desc"}).find("span").get_text()

    def _set_season_episodes(self, soup: BeautifulSoup):
        return soup.find("ul", attrs={"class": "content_playlist"}).find_all("li")

    def _set_season_year(self, soup: BeautifulSoup):
        return soup.find(
            "a", {"href": re.compile(r"/index.php/vod/search/year/[0-9]{4}.html")}
        ).get_text()

    ######## FETCH EPISODE M3U8 ########

    def _episode_url(self, relative_episode_url: str) -> str:
        return "https://www.olevod.com" + relative_episode_url

    def _set_episode_script(self, episode_soup: BeautifulSoup) -> str:
        return str(
            episode_soup.find("div", attrs={"class": "player_video"}).find("script")
        )

    def _set_episode_m3u8(self, episode_script: str) -> str:
        return re.findall(
            r"https:\\\/\\\/europe.olemovienews.com[\w\d\/\\\.]*.m3u8", episode_script
        )[0].replace("\\", "")

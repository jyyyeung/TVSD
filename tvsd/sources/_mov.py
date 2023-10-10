import re
from typing import Any

from bs4 import BeautifulSoup, ResultSet, Tag

from tvsd.sources.base import Source

__status__ = "Development"


class Mov(Source):
    """Mov class"""

    ### SEARCHING FOR A SHOW ###

    def _search_url(self, search_query: str) -> str:
        return f"https://ww1.new-movies123.co/search/{search_query}"

    def _get_query_results(self, query_result_soup: BeautifulSoup) -> ResultSet[Any]:
        return query_result_soup.find_all("a", attrs={"class": "item_series"})

    ##### PARSE EPISODE DETAILS FROM URL #####

    def _set_season_title(self, soup: BeautifulSoup):
        return None

    def _set_relative_episode_url(self, soup: Tag) -> str:
        return None

    ##### PARSE SEASON FROM QUERY RESULT #####

    def _get_result_note(self, query_result: BeautifulSoup) -> str:
        return None

    def _get_result_details_url(self, query_result: BeautifulSoup) -> str:
        return f'https://ww1.new-movies123.co{query_result["href"]}'

    #### PARSE SEASON DETAILS FROM DETAILS URL ####

    def _set_episode_title(self, soup: Tag) -> str:
        return None

    def _set_season_description(self, soup: BeautifulSoup):
        return None

    def _set_season_episodes(self, soup: BeautifulSoup):
        return soup.find(
            "div", attrs={"aria-labelledby": "episodes-select-tab"}
        ).find_all("a")

    def _set_season_year(self, soup: BeautifulSoup):
        return soup.find("a", {"href": re.compile(r"/year/[0-9]{4}")}).get_text()

    ######## FETCH EPISODE M3U8 ########

    def _episode_url(self, relative_episode_url: str) -> str:
        # BUG: Can't find link to good quality video
        return None

    def _set_episode_script(self, episode_soup: BeautifulSoup) -> str:
        return None

    def _set_episode_m3u8(self, episode_script: str) -> str:
        return None

from difflib import SequenceMatcher
import os
from typing import TYPE_CHECKING, Any, Literal, Union, List
from bs4 import PageElement

import typer
from tvsd.sources.xiao_bao import XiaoBao

from tvsd.sources.olevod import OLEVOD

from tvsd.utils import LOGGER

if TYPE_CHECKING:
    from tvsd.season import Season
    from tvsd.show import Show


class SearchQuery:
    """Searches for a show based on query"""

    def __init__(self, query: str):
        self._query: str = query
        self._results = []
        self._exists_locally = False
        self._chosen_show = None

    def find_show(self, base_path: str):
        """Finds show information locally or online

        Args:
            base_path (str): Base path to local media directory
        """
        if False:
            self.check_local_shows(base_path)

        if not self._exists_locally or self._chosen_show is None:
            self.find_shows_online()

        # TODO: if searched result is from database, get source from db
        self._chosen_show.fetch_details()

        return self._chosen_show

    def check_local_shows(self, base_path: str):
        """Checks if show exists locally in directory

        Args:
            base_path (str): Base path to local media directory
        """
        # dir loop check dir
        for directory in os.listdir(base_path + "/TV Series/"):
            season_title = directory.split(" ")[0]
            similarity_ratio = SequenceMatcher(None, self._query, season_title).ratio()

            # If directory name is similar to query
            if similarity_ratio >= 0.8:
                # print(season_title, similarity_ratio)
                if (
                    typer.prompt(
                        text=f"Are you looking for {directory}?", type=str, default="n"
                    ).capitalize()
                    == "Y"
                ):
                    self._exists_locally = True
                    # TODO: Complete this
                    # self._chosen_show = utils.load_source_details(
                    #     base_path + "/TV Series/" + directory
                    # )

    def find_shows_online(self):
        """Searches for shows online and returns a list of shows"""

        result: Union[PageElement, Any]
        # for result in query_results:
        #     result_index += 1

        query_results: List[Literal["Show"], Literal["Season"]] = []
        # TODO: Search in db first / or put db results first

        LOGGER.debug("Searching for %s", self._query)

        query_results += OLEVOD().query_from_source(self._query)
        query_results += XiaoBao().query_from_source(self._query)
        # query_results += BuDing3.search_bu_ding3(query)
        # query_results += MOV.search_mov(query)
        # query_results += YingHua.search_yinghua(query)
        # query_results += IFY.search_iyf(self._query)

        # enumerate results for printing
        for result_index, result in enumerate(query_results):
            print(result_index, result.title, result.source.source_name, result.note)

        self._chosen_show = query_results[typer.prompt(text="请选择你下载的节目", type=int)]

    @property
    def chosen_show(self) -> Literal["Show"] | Literal["Season"]:
        """Returns the chosen show

        Returns:
            Union["Show", "Season"]: Chosen show
        """
        return self._chosen_show

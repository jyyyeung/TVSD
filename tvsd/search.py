import importlib
import inspect
import logging
import os
import pkgutil
import sys
from difflib import SequenceMatcher
from typing import TYPE_CHECKING, List

import typer
from rich.console import Console
from rich.table import Table

from tvsd import sources
from tvsd._variables import state_series_dir

# from tvsd.sources import *
from tvsd.sources.base import Source

if TYPE_CHECKING:
    from tvsd.types.season import Season
    from tvsd.types.show import Show

console = Console()


class SearchQuery:
    """Searches for a show based on query"""

    def __init__(self, query: str):
        self._query: str = query
        self._exists_locally = False
        self._chosen_show = None

    def find_show(self, base_path: str):
        """Finds show information locally or online

        Args:
            base_path (str): Base path to local media directory
        """
        # if False:
        # self.check_local_shows(base_path)

        if not self._exists_locally or self._chosen_show is None:
            self.find_shows_online()

        if self._chosen_show is None:
            raise ValueError("No show found")

        # TODO: if searched result is from database, get source from db
        self._chosen_show.fetch_details()

        return self._chosen_show

    def check_local_shows(self, base_path: str):
        """Checks if show exists locally in directory

        Args:
            base_path (str): Base path to local media directory
        """
        # dir loop check dir
        for directory in os.listdir(os.path.join(base_path, state_series_dir())):
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

        query_results: List[Season] = []
        # TODO: Search in db first / or put db results first

        logging.debug("Searching for %s", self._query)

        for _, module_name, __ in pkgutil.walk_packages(sources.__path__):
            logging.debug("Found %s...", module_name)
            # Ignore template files
            if module_name.startswith("_"):
                continue
            importlib.import_module(f"tvsd.sources.{module_name}")
            for cls_name, cls_obj in inspect.getmembers(
                sys.modules[f"tvsd.sources.{module_name}"]
            ):
                # Identify module class is not base class and is a class
                if cls_name == "Source" or not inspect.isclass(cls_obj):
                    continue
                # Source is active
                if issubclass(cls_obj, Source) and cls_obj().__status__ == "active":
                    query_results += cls_obj().query_from_source(self._query)

        table = Table("index", "Title", "Source", "Note")

        for result_index, result in enumerate(query_results):
            table.add_row(
                str(result_index),
                result.title,
                result.source.source_name,
                result.note,
            )

        console.print(table)
        self._chosen_show = query_results[typer.prompt(text="请选择你下载的节目", type=int)]

    @property
    def chosen_show(self) -> "Season":
        """
        chosen_show Returns the chosen show

        Raises:
            ValueError: If no show is chosen

        Returns:
            Season: Chosen show
        """
        if self._chosen_show is None:
            raise ValueError("No show chosen")
        return self._chosen_show

"""
TYSD Show Class, parent of Seasons
Currently not used a lot, will consider removing
"""
import os
from typing import TYPE_CHECKING, List

from tvsd._variables import state_series_dir

if TYPE_CHECKING:
    from tvsd.sources.base import Source
    from tvsd.types.season import Season


class Show:
    """Contains a Show"""

    def __init__(self, source: "Source", title: str = "", begin_year: str = ""):
        self._title = title
        self._source = source
        self._seasons: List["Season"] = []
        self._begin_year = begin_year

        self._prefix = self.generate_show_prefix()

    @property
    def seasons(self) -> List["Season"]:
        """seasons of the show



        Returns:
            List[Season]: seasons of the show
        """
        return self._seasons

    @property
    def title(self) -> str:  # This getter method name is *the* name
        """Get the title of the show

        Returns:
            str: Title of the show
        """

        return self._title

    @title.setter  # the property decorates with `.setter` now
    def title(self, title):  # name, e.g. "attribute", is the same
        self._title = title  # the "value" name isn't special

    @property
    def begin_year(self) -> str:
        """Returns the begin year of the show

        Returns:
            str: begin year of the show
        """
        return self._begin_year

    def generate_show_prefix(self) -> str:
        """generate show prefix (the directory name of the show)

        Returns:
            str: show prefix (the directory name of the show)
        """

        show_title = self._title.partition(" 第")[0]

        show_prefix: str = show_title + " (" + str(self.begin_year) + ")"
        self._prefix = show_prefix
        return show_prefix

    @property
    def show_prefix(self) -> str:
        """show prefix (the directory name of the show)

        Returns:
            str: show prefix (the directory name of the show)
        """
        return self._prefix if self._prefix is not None else self.generate_show_prefix()

    @property
    def source(self) -> str:  # This getter method name is *the* name
        """source of current Show

        Returns:
            str: source of current Show
        """
        return self._source.source_name

    @property
    def relative_show_dir(self) -> str:
        """get relative directory of show in media directory from base path

        Returns:
            str: relative directory of show in media directory from base path
        """

        # relative directory of show in media directory from base path
        return os.path.join(state_series_dir(), self._prefix)

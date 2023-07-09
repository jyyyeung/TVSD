import os
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from tvsd.source import Source
    from tvsd.season import Season


class Show:
    """Contains a Show"""

    def __init__(self, source: "Source", title: str = None, begin_year: str = None):
        self._title = title
        self._source = source
        self._seasons: Union([Season], []) = []
        self._begin_year = begin_year

        self._prefix = self.generate_show_prefix()

    @property
    def title(self):  # This getter method name is *the* name
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
        return self._source

    @property
    def relative_show_dir(self) -> str:
        """get relative directory of show in media directory from base path

        Returns:
            str: relative directory of show in media directory from base path
        """

        # relative directory of show in media directory from base path
        return os.path.join("TV Series/", self._prefix)

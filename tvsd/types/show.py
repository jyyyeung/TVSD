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
    """Represents a TV show.

    Attributes:
        _title (str): The title of the show.
        _source (Source): The source of the show.
        _seasons (List[Season]): The seasons of the show.
        _begin_year (str): The year the show began.
        _prefix (str): The directory name of the show.
    """

    def __init__(self, source: "Source", title: str = "", begin_year: str = ""):
        """
        Initializes a new instance of the Show class.

        Args:
            source (Source): The source of the show.
            title (str, optional): The title of the show. Defaults to "".
            begin_year (str, optional): The year the show began. Defaults to "".
        """
        self._title = title
        self._source = source
        self._seasons: List["Season"] = []
        self._begin_year = begin_year

        self._prefix = self.generate_show_prefix()

    @property
    def seasons(self) -> List["Season"]:
        """Returns a list of all the seasons of the show.

        Returns:
            List[Season]: A list of all the seasons of the show.
        """
        return self._seasons

    @property
    def title(self) -> str:
        """Get the title of the show

        This method returns the title of the show.

        Returns:
            str: Title of the show
        """

        return self._title

    @title.setter  # the property decorates with `.setter` now
    def title(self, title):
        """
        Set the title of the show.

        Args:
            title (str): The title of the show.

        Returns:
            None
        """
        self._title = title

    @property
    def begin_year(self) -> str:
        """Returns the begin year of the show

        Returns:
            str: begin year of the show
        """
        return self._begin_year

    def generate_show_prefix(self) -> str:
        """Generate the prefix for the show.

        The prefix is the directory name of the show, and is generated by combining the show's title and beginning year.

        Returns:
            str: The prefix for the show.
        """

        show_title = self._title.partition(" 第")[0]

        show_prefix: str = show_title + " (" + str(self.begin_year) + ")"
        self._prefix = show_prefix
        return show_prefix

    @property
    def show_prefix(self) -> str:
        """
        Returns the show prefix, which is the directory name of the show.

        If the show prefix has already been set, it will be returned. Otherwise, it will be generated
        using the generate_show_prefix method.

        Returns:
            str: The show prefix (the directory name of the show).
        """
        return self._prefix if self._prefix is not None else self.generate_show_prefix()

    @property
    def source(self) -> str:
        """Getter method for the source of the current Show.

        Returns:
            str: The source of the current Show.
        """
        return self._source.source_name

    @property
    def relative_show_dir(self) -> str:
        """Get the relative directory of the show in the media directory from the base path.

        This method returns the relative directory of the show in the media directory from the base path.

        Returns:
            str: The relative directory of the show in the media directory from the base path.
        """

        # Relative directory of show in media directory from base path
        return os.path.join(state_series_dir(), self._prefix)

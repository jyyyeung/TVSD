"""
TVSD Season class, parent of Episodes
"""

import logging
import os
from typing import TYPE_CHECKING, Callable, List

import typer

from tvsd._variables import state_specials_dir
from tvsd.types.episode import Episode
from tvsd.types.show import Show

if TYPE_CHECKING:
    from tvsd.sources.base import Source
    from tvsd.types import SeasonDetailsFromURL


def check_season_index(show_title: str) -> int:
    """
    Checks the season number for a particular show based on the show title.

    Args:
        show_title (str): The title of the show to check.

    Returns:
        int: The index of the season identified from the title.
    """
    season_index = 1
    print(show_title)
    if "第" in show_title:
        if "第一季" in show_title:
            season_index = 1
        elif "第二季" in show_title:
            season_index = 2
        elif "第三季" in show_title:
            season_index = 3
        elif "第四季" in show_title:
            season_index = 4
        elif "第五季" in show_title:
            season_index = 5
        elif "第六季" in show_title:
            season_index = 6
        elif "第七季" in show_title:
            season_index = 7
        elif "第八季" in show_title:
            season_index = 8
        elif "第九季" in show_title:
            season_index = 9
    elif "Season" in show_title:
        season_index = int(show_title.lower().split("season")[-1])
    elif "part" in show_title:
        season_index = 1
    elif typer.prompt("这个节目是否续季？（not S1)", default="").capitalize() == "Y":
        season_index: int = typer.prompt(text="这个节目是第几季？", type=int)
    else:
        season_index = 1
    return season_index


class Season:
    """Represents a season of a TV show.

    Attributes:
        fetch_episode_m3u8 (Callable): A function that fetches the m3u8 file for an episode.
        episodes (List[Episode]): A list of episodes in the season.
        details (SeasonDetailsFromURL): Details about the season.
        source (Source): The source of the season.
        note (str): A note about the season.
        details_url (str): The URL for the details of the season.
    """

    def __init__(
        self,
        fetch_episode_m3u8: Callable,
        episodes: List["Episode"],
        details: "SeasonDetailsFromURL",
        source: "Source",
        note: str = "",
        details_url: str = "",
    ) -> None:
        """
        Initializes a Season object.

        Args:
            fetch_episode_m3u8 (Callable): A callable function that fetches the m3u8 file for an episode.
            episodes (List[Episode]): A list of Episode objects.
            details (SeasonDetailsFromURL): A dictionary containing details about the season.
            source (Source): A Source object representing the source of the season.
            note (str, optional): A note about the season. Defaults to "".
            details_url (str, optional): The URL of the page containing details about the season. Defaults to "".
        """
        season_title: str = details["title"]
        self._episodes: List["Episode"] = episodes
        self._title: str = season_title
        self._year: str = details["year"]
        self._description: str = details["description"]
        self._index: int | None = None

        self._details_url: str = details_url
        # self._source_id = source_id
        self._note: str = note
        self._source: Source = source
        self._show: Show

        self._fetch_episode_m3u8 = fetch_episode_m3u8

    def fetch_details(self) -> None:
        """Fetch details for season for download.

        This method creates a show, generates episodes, and fetches details for the season
        to prepare for download.
        """
        self.create_show()
        # self.determine_season_index(self._title)
        self.generate_episodes()

    def generate_episodes(self) -> None:
        """Generate Episode objects for the season.

        This method generates Episode objects for the season based on the list of episodes
        associated with the season. If an episode in the list is already an Episode object,
        it is added to the list of generated Episode objects. If an episode in the list is
        not an Episode object, its details are parsed from the source and a new Episode
        object is created and added to the list of generated Episode objects.

        Returns:
            None
        """
        episode_objects: List["Episode"] = []
        for episode in self._episodes:
            if isinstance(episode, Episode):
                episode_object: "Episode" = episode
            else:
                episode_details = self._source.parse_episode_details_from_li(episode)
                episode_object = Episode(
                    episode_name=episode_details["title"],
                    season=self,
                    episode_url=episode_details["url"],
                )

            episode_objects.append(episode_object)
        self._episodes = episode_objects

    @property
    def episodes(self) -> List["Episode"]:
        """
        Returns the list of episodes in the season.

        Returns:
            List[Episode]: A list of Episode objects representing the episodes in the season.
        """
        return self._episodes

    def create_show(self) -> "Show":
        """
        Create a parent show for this season.

        This method creates a parent show for the current season object. The parent show is created using the
        source type, title, and beginning year of the current season. The created show is then returned.

        Returns:
            Show: The created parent show.
        """
        show = Show(type(self._source), self._title, self.determine_show_begin_year())
        self._show = show
        return show

    def determine_season_index(self, season_title: str) -> int:
        """Determines season index from title of season

        Args:
            season_title (str, optional): Title of the season to query with. Defaults to None.

        Returns:
            int: index of season
        """
        season_index: int = check_season_index(season_title)
        season_index = typer.prompt(
            text="Fix the season index? ", default=season_index, type=int
        )
        self._index = season_index
        return season_index

    @property
    def season_index(self) -> int:
        """Returns the season index

        This method returns the index of the season. If the index has not been set yet, it will be determined
        based on the title of the season. If the title does not contain a season index, the default index of 1
        will be returned.

        Returns:
            int: season index
        """
        if self._index is None:
            self.determine_season_index(self._title)

        return self._index or 1

    @property
    def relative_season_dir(self) -> str:
        """Returns the relative directory for the current season.

        If the season index is 0, the relative specials directory is returned.
        Otherwise, the relative directory for the current season is returned.

        Returns:
            str: The relative directory for the current season.
        """
        if self.season_index == 0:
            return self.relative_specials_dir
        return os.path.join(
            self._show.relative_show_dir, f"Season {str(self.season_index).zfill(2)}"
        )

    @property
    def relative_specials_dir(self) -> str:
        """Returns the relative specials directory

        This method returns the relative directory for the specials of the season.

        Returns:
            str: relative specials directory
        """
        return os.path.join(self._show.relative_show_dir, state_specials_dir())

    def determine_show_begin_year(self) -> str:
        """Query the begin year of the show

        This method determines the begin year of the show based on the season's year and index.
        If the season index is greater than 1, it prompts the user to input the year of the first season.

        Returns:
            str: Begin year of the show as a string
        """
        print(self.year)
        season_year = int(self.year)
        show_year: int = season_year

        if self.season_index > 1:
            # TODO: Auto

            show_year = season_year - self.season_index + 1
            show_year = typer.prompt(
                text=f"第一季在那一年？(calculated={show_year})",
                type=int,
                default=show_year,
            )
        # self.begin_year = season_year

        return str(show_year)

    @property
    def year(self) -> str:
        """Returns the year of the season

        Returns:
            str: year of the season
        """
        logging.info(self)
        return self._year

    @property
    def note(self) -> str:
        """Get the note of the show

        This method returns the note of the show.

        Returns:
            str: Note of the show
        """

        return self._note

    @note.setter  # the property decorates with `.setter` now
    def note(self, note) -> None:  # name, e.g. "attribute", is the same
        self._note = note  # the "value" name isn't special

    @property
    def details_url(self) -> str:  # This getter method name is *the* name
        """Returns the details url of the season

        Returns:
            str: details url of the season
        """
        return self._details_url

    @details_url.setter  # the property decorates with `.setter` now
    def details_url(self, details_url) -> None:  # name, e.g. "attribute", is the same
        self._details_url = details_url  # the "value" name isn't special

    @property
    def title(self) -> str:
        """Returns the title of the season

        Returns:
            str: title of the season
        """
        return self._title

    @property
    def show(self) -> "Show":
        """Returns the show of the season

        Returns:
            Show: show of the season
        """
        return self._show

    @property
    def source(self) -> "Source":
        """Returns the source of the season

        Returns:
            Source: source of the season
        """
        return self._source

    @property
    def description(self) -> str:
        """Returns the description of the season

        Returns:
            str: description of the season
        """
        return self._description

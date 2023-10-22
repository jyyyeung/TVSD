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
    """Checks if season number for a particular show

    Args:
        show_title (str): Title of show to check

    Returns:
        int: index of episode identified from title
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
        season_index = typer.prompt(text="这个节目是第几季？", type=int)
    else:
        season_index = 1
    return season_index


class Season:
    """Season class"""

    def __init__(
        self,
        fetch_episode_m3u8: Callable,
        episodes: List["Episode"],
        details: "SeasonDetailsFromURL",
        source: "Source",
        note: str = "",
        details_url: str = "",
    ) -> None:
        season_title = details["title"]
        self._episodes: List["Episode"] = episodes
        self._title = season_title
        self._year = details["year"]
        self._description = details["description"]
        self._index: int | None = None

        self._details_url = details_url
        # self._source_id = source_id
        self._note = note
        self._source = source
        self._show: Show

        self._fetch_episode_m3u8 = fetch_episode_m3u8

    def fetch_details(self) -> None:
        """Fetch details for season for download"""
        self.create_show()
        # self.determine_season_index(self._title)
        self.generate_episodes()

    def generate_episodes(self) -> None:
        """generate episodes for season"""
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
        """Returns the episodes of the season

        Returns:
            List[Episode]: episodes of the season
        """
        return self._episodes

    def create_show(self) -> "Show":
        """Create a parent show for this season

        Returns:
            Show: created parent show
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
        season_index = check_season_index(season_title)
        season_index = typer.prompt(
            text="Fix the season index? ", default=season_index, type=int
        )
        self._index = season_index
        return season_index

    @property
    def season_index(self) -> int:
        """Returns the season index

        Returns:
            int: season index
        """
        if self._index is None:
            self.determine_season_index(self._title)

        return self._index or 1

    @property
    def relative_season_dir(self) -> str:
        """Returns the relative season directory

        Returns:
            str: relative season directory
        """
        if self.season_index == 0:
            return self.relative_specials_dir
        return os.path.join(
            self._show.relative_show_dir, f"Season {str(self.season_index).zfill(2)}"
        )

    @property
    def relative_specials_dir(self) -> str:
        """Returns the relative specials directory

        Returns:
            str: relative specials directory
        """
        return os.path.join(self._show.relative_show_dir, state_specials_dir())

    def determine_show_begin_year(self) -> str:
        """Query the begin year of the show

        Returns:
            int: Begin year of the show
        """
        print(self.year)
        season_year = int(self.year)
        show_year = season_year

        if self.season_index > 1:
            # TODO: Auto

            show_year = season_year - self.season_index + 1
            show_year = typer.prompt(
                text=f"第一季在那一年？(calculated={show_year})", type=int, default=show_year
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
    def note(self) -> str:  # This getter method name is *the* name
        """Get the note of the show

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

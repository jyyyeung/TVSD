"""
TVSD Season class, parent of Episodes
"""

from __future__ import annotations
import os
from typing import TYPE_CHECKING, Callable, List

from bs4 import Tag
from pydantic import BaseModel, ConfigDict, Field
import typer


from tvsd.config import settings

from tvsd.types.episode import Episode
from tvsd.types.show import Show

from tvsd.sources.base import Source
from tvsd.types.season_details import SeasonDetailsFromURL

if TYPE_CHECKING:
    from tvsd.types.episode import Episode
    from tvsd.types.show import Show


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


def generate_episodes(
    ep_tags: List[str | Tag], source: Source, season: Season
) -> List["Episode"]:
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
    for episode_str in ep_tags:
        # if isinstance(episode, Episode):
        #     episode_object: "Episode" = episode
        # else:
        episode_details = source.parse_episode_details_from_li(episode_str)
        episode_object = Episode(
            title=episode_details["title"],
            url=episode_details["url"],
            season_info=season.get_season_info(),
        )

        episode_objects.append(episode_object)
    season.episodes = episode_objects
    return episode_objects


class SeasonInfo(BaseModel):
    """Includes information required to name a season episode file.

    Attributes:
        show_prefix (str): The prefix of the show.
        season_index (int): The index of the season.
        episode_number (int): The number of the episode.
    """

    show_prefix: str
    season_index: int
    relative_season_dir: str
    fetch_episode_m3u8: Callable
    source: Source


class Season(BaseModel):
    """Represents a season of a TV show.

    Attributes:
        fetch_episode_m3u8 (Callable): A function that fetches the m3u8 file for an episode.
        episodes (List[Episode]): A list of episodes in the season.
        details (SeasonDetailsFromURL): Details about the season.
        source (Source): The source of the season.
        note (str): A note about the season.
        details_url (str): The URL for the details of the season.
    """

    # Define Pydantic model fields
    episode_strs: List[str | Tag]
    episodes: List[Episode] = Field(default_factory=list)
    details: "SeasonDetailsFromURL"

    title: str = Field(default_factory=lambda self: self["details"].title)
    year: str = Field(default_factory=lambda self: self["details"].year)
    description: str = Field(default_factory=lambda self: self["details"].description)
    index: int | None = None
    details_url: str
    note: str | None = None
    poster_url: str | None = None
    fetch_episode_m3u8: Callable
    source: "Source"
    show: Show | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # def __init__(self, **kwargs) -> None:
    #     super().__init__(**kwargs)
    # details = kwargs["details"]
    # self.title = details.title
    # self.year = details.year
    # self.description = details.description

    def __post_init__(self) -> None:
        self.fetch_details()

    def get_season_info(self) -> SeasonInfo:
        """Get the season info for the season."""
        return SeasonInfo(
            show_prefix=self.show.prefix,
            season_index=self.season_index,
            relative_season_dir=self.relative_season_dir,
            fetch_episode_m3u8=self.source.fetch_episode_m3u8,
            source=self.source,
        )

    def fetch_details(self) -> None:
        """Fetch details for season for download.

        This method creates a show, generates episodes, and fetches details for the season
        to prepare for download.
        """
        self.create_show()
        self.episodes = generate_episodes(self.episode_strs, self.source, self)

        # self.episodes = generate_episodes(self.episodes, self.source, self)
        # self.generate_episodes()

    def add_episode(self, episode: Episode) -> None:
        """Add an episode to the season.

        This method adds an episode to the season.
        """
        self.episodes.append(episode)

    def create_show(self) -> "Show":
        """
        Create a parent show for this season.

        This method creates a parent show for the current season object. The parent show is created using the
        source type, title, and beginning year of the current season. The created show is then returned.

        Returns:
            Show: The created parent show.
        """
        show = Show(
            title=self.title,
            begin_year=self.determine_show_begin_year(),
            source=self.source,
        )
        self.show = show
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
        self.index = season_index
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
        if self.index is None:
            self.determine_season_index(self.title)

        return self.index or 1

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
            self.show.relative_show_dir, f"Season {str(self.season_index).zfill(2)}"
        )

    @property
    def relative_specials_dir(self) -> str:
        """Returns the relative specials directory

        This method returns the relative directory for the specials of the season.

        Returns:
            str: relative specials directory
        """
        return os.path.join(self.show.relative_show_dir, settings.SPECIALS_DIR)

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


SeasonInfo.model_rebuild()
Season.model_rebuild()  # Rebuild model to resolve forward references

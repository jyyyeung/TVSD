"""Custom types for TVSD """
from typing import List, TypedDict

from tvsd.types.episode import Episode
from tvsd.types.season import Season
from tvsd.types.show import Show

__all__ = ["Episode", "Season", "Show", "SeasonDetailsFromURL", "EpisodeDetailsFromURL"]


class SeasonDetailsFromURL(TypedDict):
    """DetailsFromURL type object

    Attributes:
        title (str): The title of the season.
        description (str): The description of the season.
        episodes (List[Episode]): A list of Episode objects representing the episodes in the season.
        year (str): The year the season was released.
    """

    title: str
    description: str
    episodes: List["Episode"]
    year: str


class EpisodeDetailsFromURL(TypedDict):
    """DetailsFromURL type object

    Attributes:
        title (str): The title of the episode
        url (str): The URL of the episode
    """

    title: str
    url: str

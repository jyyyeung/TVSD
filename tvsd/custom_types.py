"""Custom types for TVSD """
from typing import TYPE_CHECKING, List, TypedDict

if TYPE_CHECKING:
    from tvsd.episode import Episode


class SeasonDetailsFromURL(TypedDict):
    """DetailsFromURL type object

    Args:
        TypedDict (TypedDict): TypedDict from typings package
    """

    title: str
    description: str
    episodes: List["Episode"]
    year: str


class EpisodeDetailsFromURL(TypedDict):
    """DetailsFromURL type object

    Args:
        TypedDict (TypedDict): TypedDict from typings package
    """

    title: str
    url: str

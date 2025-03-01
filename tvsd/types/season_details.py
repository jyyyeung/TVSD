from __future__ import annotations
from dataclasses import dataclass
from typing import List

from bs4 import Tag


@dataclass
class SeasonDetailsFromURL:
    """DetailsFromURL type object

    Attributes:
        title (str): The title of the season.
        description (str): The description of the season.
        episode_strs (List[str]): List of episode strings in the season
        year (str): The year the season was released
        poster_url (str): URL for the season poster image
    """

    title: str
    description: str
    episode_strs: List[str | Tag]
    year: str
    poster_url: str

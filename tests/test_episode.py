"""Unit tests for the Episode number/filename logic (no network)."""

import pytest

from tvsd.types.episode import Episode


class FakeShow:
    """Minimal stand-in for Show, only what Episode.filename needs."""

    show_prefix = "庆余年 (2019)"


class FakeSeason:
    """Minimal stand-in for Season, only what Episode needs."""

    season_index = 2
    show = FakeShow()

    def __init__(self) -> None:
        self.episodes = []


@pytest.mark.parametrize(
    ("episode_name", "expected_number"),
    [
        ("第01集", 1),
        ("第12集", 12),
        ("12", 12),
        ("第3期上", 3),
    ],
)
def test_episode_number_is_identified_from_name(episode_name, expected_number):
    episode = Episode(episode_name=episode_name, episode_url="", season=FakeSeason())
    assert episode.episode_number == expected_number


def test_episode_number_defaults_to_one_when_unparsable():
    episode = Episode(episode_name="预告片", episode_url="", season=FakeSeason())
    assert episode.episode_number == 1


def test_filename_does_not_raise_before_number_is_set():
    """Regression: `_number` used to be a bare annotation, so this raised AttributeError."""
    episode = Episode(episode_name="第05集", episode_url="", season=FakeSeason())

    assert episode.filename == "庆余年 (2019) - S02E05 - 第05集"


def test_specials_use_season_zero_in_filename():
    """`is_specials` means "the name is not a numbered episode", so it lands in Season 00."""
    episode = Episode(episode_name="特别篇", episode_url="", season=FakeSeason())

    assert episode.is_specials is True
    assert episode.filename == "庆余年 (2019) - S00E01 - 特别篇"


def test_dated_episode_names_stay_in_the_regular_season():
    """Sites list variety episodes as YYYYMMDD, so those must not be treated as specials."""
    episode = Episode(episode_name="20240101", episode_url="", season=FakeSeason())

    assert episode.is_specials is False
    assert episode.filename == "庆余年 (2019) - S02E01 - 20240101"

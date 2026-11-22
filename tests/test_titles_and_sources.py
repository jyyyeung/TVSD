"""Unit tests for Plex title cleanup and source filtering (no network)."""

import pytest

from tvsd.search import _normalise_source_name, _source_enabled
from tvsd.sources.olevod import OLEVOD
from tvsd.sources.xiao_bao import XiaoBao, _clean_season_title


@pytest.mark.parametrize(
    ("raw_title", "expected"),
    [
        (
            "庆余年第二季(2024) 已完结 免费在线观看 - 小宝影院",
            "庆余年 第二季",
        ),
        (
            "庆余年 第二季(2024) 已完结 免费在线观看 - 小宝影院 - 在线视频",
            "庆余年 第二季",
        ),
        ("繁花(2023) 更新至30集 高清完整版 - 小宝影院", "繁花"),
        ("庆余年 - 小宝影院 - 在线视频", "庆余年"),
    ],
)
def test_clean_season_title_strips_site_noise(raw_title, expected):
    assert _clean_season_title(raw_title) == expected


def test_clean_season_title_keeps_season_marker_for_season_detection():
    """check_season_index reads `第N季` from the title, and Show.generate_show_prefix
    drops everything from ' 第' onwards, so the space in front of it is load-bearing."""
    cleaned = _clean_season_title("庆余年第二季(2024) 已完结 - 小宝影院")

    assert "第二季" in cleaned
    assert cleaned.partition(" 第")[0] == "庆余年"


def test_normalise_source_name_matches_settings_spelling():
    assert _normalise_source_name("XiaoBao") == _normalise_source_name("xiao_bao")
    assert _normalise_source_name("OLEVOD") == "olevod"


def test_source_enabled_uses_normalised_names():
    assert _source_enabled(XiaoBao()) is True


def test_dead_sources_are_never_queried():
    assert OLEVOD().__status__ == "dead"
    assert _source_enabled(OLEVOD()) is False

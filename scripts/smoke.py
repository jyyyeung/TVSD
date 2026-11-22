#!/usr/bin/env python3
"""TVSD live smoke test.

Answers one question: *what is still working?* Run it after a long pause to see
which layer rotted, instead of rediscovering it while trying to download an
episode.

Checks, in order of how cheap they are to fix:
  engine   - ffmpeg + yt-dlp present (system prerequisites)
  config   - settings load, media/temp dirs usable
  sources  - which sources are active, which are marked dead
  search   - live search returns results on an active source
  details  - details page still parses (title, year, episodes)
  m3u8     - the first episode still resolves to a playable m3u8

Usage:
    python scripts/smoke.py            # checks everything, downloads nothing
    python scripts/smoke.py --query 繁花

Exit code 0 when all checks pass, 1 when any of them fails.
"""

import argparse
import sys
import traceback
from typing import Callable, List, Tuple

sys.path.insert(0, ".")

from tvsd.config import settings  # noqa: E402
from tvsd.downloader import DownloadEngineError, check_engine  # noqa: E402
from tvsd.sources.base import Source  # noqa: E402

DEFAULT_QUERY = "庆余年"

PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"


class Skip(Exception):
    """Raised when a check cannot run because an earlier one already failed."""

results: List[Tuple[str, str, str]] = []


def check(name: str, description: str, func: Callable[[], str]) -> bool:
    """Run one check, record its verdict and return whether it passed."""
    try:
        detail = func()
    except DownloadEngineError as error:
        results.append((name, FAIL, str(error)))
        return False
    except Skip as reason:
        results.append((name, SKIP, str(reason)))
        return True
    except Exception as error:  # noqa: BLE001 - a smoke test reports, it does not raise
        results.append((name, FAIL, f"{type(error).__name__}: {error}"))
        traceback.print_exc(limit=2)
        return False

    results.append((name, PASS, detail or description))
    return True


def check_version() -> str:
    from tvsd import __version__

    return f"tvsd {__version__}"


def check_config() -> str:
    return (
        f"media_root={settings.MEDIA_ROOT} temp_root={settings.TEMP_ROOT} "
        f"series_dir={settings.SERIES_DIR}"
    )


def check_sources() -> str:

    active, dead = [], []
    for source_class in _iter_source_classes():
        (active if source_class().__status__ == "active" else dead).append(
            source_class.__name__
        )
    if not active:
        raise RuntimeError(f"no active source (dead: {dead})")

    return f"active={active} dead={dead}"


def _iter_source_classes() -> list:
    """Every Source subclass that lives in a non-underscore source module."""
    import importlib
    import inspect
    import pkgutil

    from tvsd import sources

    classes = []
    for _, module_name, _ in pkgutil.walk_packages(sources.__path__):
        if module_name.startswith("_"):
            continue
        module = importlib.import_module(f"tvsd.sources.{module_name}")
        for _, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, Source)
                and obj is not Source
                and obj.__module__ == module.__name__
            ):
                classes.append(obj)
    return classes


VERDICT_PARSE = "parse"
VERDICT_BLOCKED = "blocked"


def diagnose_empty_search(source: Source, query: str) -> Tuple[str, str]:
    """Say why a search returned nothing, and whether the page was even readable.

    Returns:
        Tuple[str, str]: VERDICT_PARSE when the page came back and can be judged,
        VERDICT_BLOCKED when it did not, plus a human-readable reason.
    """
    from tvsd.utils import SCRAPER

    url = source._search_url(query)  # noqa: SLF001 - the smoke test reports on internals
    try:
        response = SCRAPER.get(url, timeout=25)
    except Exception as error:  # noqa: BLE001 - the whole point is to report it
        return VERDICT_BLOCKED, f"search page unreachable ({type(error).__name__}: {error})"
    if response.status_code != 200:
        return (
            VERDICT_BLOCKED,
            f"search page returned HTTP {response.status_code}, which looks like blocking",
        )
    body = response.text or ""
    if "clearfix" in body:
        return (
            VERDICT_PARSE,
            "the page came back with its result-list markup, so nothing was parsed out of it "
            "(the parser broke, or this query has no matches)",
        )
    return (
        VERDICT_PARSE,
        f"HTTP 200 but no result markup at all ({len(body)} bytes); "
        "the site serves something other than a result list",
    )

def make_live_checks(query: str) -> List[Tuple[str, str, Callable[[], str]]]:
    """Build the network checks around one chosen source and query."""

    state = {}

    def live_sources():
        from tvsd.search import _source_enabled

        return [cls() for cls in _iter_source_classes() if _source_enabled(cls())]

    def search() -> str:
        candidates = live_sources()
        if not candidates:
            raise RuntimeError("no active source to search")
        state["source"] = candidates[0]
        matches = candidates[0].query_from_source(query)
        if not matches:
            verdict, reason = diagnose_empty_search(candidates[0], query)
            message = f"0 results for {query!r} on {candidates[0].source_name}: {reason}"
            if verdict == VERDICT_BLOCKED:
                raise Skip(f"{message} (unverifiable from this network; run `make smoke` locally)")
            raise RuntimeError(message)
        state["matches"] = matches
        return f"{len(matches)} results for {query!r} on {candidates[0].source_name}"

    def details() -> str:
        if "matches" not in state:
            raise Skip("search yielded nothing to inspect")
        season = state["matches"][0]
        season.fetch_details()
        state["season"] = season
        if not season.episodes:
            raise RuntimeError("details page parsed but yielded 0 episodes")
        return (
            f"{season.title!r} year={season.year} episodes={len(season.episodes)} "
            f"first={season.episodes[0].name!r}"
        )

    def m3u8() -> str:
        if "season" not in state:
            raise Skip("details page was not parsed")
        episode = state["season"].episodes[0]
        url = episode.fetch_episode_m3u8_url
        if not url or "m3u8" not in url:
            raise RuntimeError(f"no m3u8 url extracted (got {url!r})")
        return url

    def plex_name() -> str:
        if "season" not in state:
            raise Skip("details page was not parsed")
        episode = state["season"].episodes[0]
        return episode.filename

    return [
        ("search", f"live search for {query!r}", search),
        ("details", "details page parses", details),
        ("m3u8", "first episode resolves an m3u8", m3u8),
        ("naming", "Plex filename is generated", plex_name),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--query",
        default=DEFAULT_QUERY,
        help=f"show to search for (default: {DEFAULT_QUERY})",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="skip the network checks (search/details/m3u8)",
    )
    arguments = parser.parse_args()

    check("engine", "ffmpeg and yt-dlp on PATH", lambda: str(check_engine()))
    check("config", "settings load", check_config)
    check("sources", "source statuses", check_sources)

    if arguments.offline:
        results.append(("network", SKIP, "--offline"))
    else:
        for name, description, func in make_live_checks(arguments.query):
            check(name, description, func)

    width = max(len(name) for name, _, _ in results)
    print()
    for name, verdict, detail in results:
        print(f"{name.ljust(width)}  {verdict:4}  {detail}")

    failed = [name for name, verdict, _ in results if verdict == FAIL]
    print()
    if failed:
        print(f"[FAILED] {len(failed)} check(s): {', '.join(failed)}")
        return 1

    print("[OK] everything above is working")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

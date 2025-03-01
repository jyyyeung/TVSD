import logging
from typing import List

from bs4 import BeautifulSoup
import chinese_converter

from tvsd.sources.base import Source
from tvsd.types.season import Season, SeasonInfo
from tvsd.types.season_details import SeasonDetailsFromURL


def query_from_source(
    source: Source, search_query: str, is_interactive: bool = True
) -> List["Season"]:
    """
    query_from_source Searches for a show

    Args:
        search_query (str): Query to search for

    Returns:
        List[Season]: List of shows
    """
    _result_list: List[Season] = []
    if source.is_simplified:
        search_query = chinese_converter.to_simplified(search_query)
    if source.is_traditional:
        search_query = chinese_converter.to_traditional(search_query)

    search_url = source._search_url(search_query)

    logging.info("Searching %s...", {search_query})
    logging.debug("Searching for %s in %s", search_query, search_url)

    query_result_soup = source.get_query_result_soup(search_url)
    if query_result_soup is not None:
        query_results = source._get_query_results(query_result_soup)
        # Below are same for all

        for result in query_results:
            show = season_from_query_result(source, result, is_interactive)
            if show is not None:
                _result_list.append(show)

    if len(_result_list) == 0 and len(source.domains) > source._domain_index + 1:
        source._domain_index += 1
        return query_from_source(source, search_query, is_interactive)

    return _result_list


def season_from_query_result(
    source: Source, query_result: BeautifulSoup, is_interactive: bool = True
) -> Season:
    """
    season_from_query_result Parses a query result into a Season object

    Args:
        query_result (BeautifulSoup): Query result
    """
    from tvsd.types.season import Season

    details_url = source._get_result_details_url(query_result)
    if details_url is None:
        return None

    note = source._get_result_note(query_result)
    details = parse_season_from_details_url(source, details_url)
    if details is None:
        return None
    season = Season(
        note=note,
        details=details,
        details_url=details_url,
        fetch_episode_m3u8=source.fetch_episode_m3u8,
        episode_strs=details.episode_strs,
        source=source,
        poster_url=details.poster_url,
        is_interactive=is_interactive,
    )
    return season


def parse_season_from_details_url(
    source: Source, season_url: str
) -> "SeasonDetailsFromURL | None":
    """Parses details from details url

    Args:
        details_url (str, optional): Details url to the result page. Defaults to None.

    Returns:
        dict: Details found on the details page
    """
    soup = source.fetch_details_soup(season_url)
    if soup is None:
        return None
    details: SeasonDetailsFromURL = SeasonDetailsFromURL(
        title=chinese_converter.to_simplified(source._set_season_title(soup)),
        description=source._set_season_description(soup),
        episode_strs=source._set_season_episodes(soup),
        year=source._set_season_year(soup),
        poster_url=source._set_season_poster_url(soup),
    )

    # print("Method for finding details from this source is undefined...")
    return details


def fetch_episode_m3u8_url(source: Source, episode_url: str) -> str:
    """Fetches the m3u8 url for an episode

    Args:
        episode_url (str): The url of the episode
    """
    return source.fetch_episode_m3u8(episode_url)

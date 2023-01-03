from typing import Any

import cloudscraper
import requests
from bs4 import BeautifulSoup, ResultSet

from Show import Show, Source
from fake_useragent import UserAgent

ua = UserAgent()


def search_123mov(query: str) -> [Show]:
    search_url: str = f"https://ww1.new-movies123.co/search/{query}"
    scraper = cloudscraper.create_scraper(delay=10, browser={ 'custom': 'ScraperBot/1.0', })
    search_result_page = scraper.get(search_url).content
    query_result_soup: BeautifulSoup = BeautifulSoup(search_result_page, 'html.parser')
    query_results: ResultSet[Any] = query_result_soup.find_all('a', attrs={ 'class': 'item_series' })
    result_list = []
    result_index: int = 1

    for result in query_results:
        show = Show(result, Source.MOV)
        result_list.append(show)
    return result_list

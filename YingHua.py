from typing import Any

import requests
from bs4 import BeautifulSoup, ResultSet

from Show import Show, Source


def search_yinghua(query: str) -> [Show]:
    search_url: str = f"https://www.yhdmp.cc/s_all?ex=1&kw={query}"
    search_result_page: bytes = requests.get(search_url,
                                             headers={ 'User-Agent': 'Mozilla/5.0' }).content
    query_result_soup: BeautifulSoup = BeautifulSoup(search_result_page, 'html.parser')
    # print(query_result_soup)
    # BUG: Does not work cuz of cloudflare
    query_results: ResultSet[Any] = query_result_soup.find('div', attrs={ 'class': 'lpic' }).findChildren('li')
    result_list = []
    result_index: int = 1

    for result in query_results:
        print(result)
        show = Show(result, Source.YingHua)
        result_list.append(show)
    return result_list

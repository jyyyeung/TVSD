import re
from typing import Any

import requests
from bs4 import BeautifulSoup, ResultSet

from Show import Show, Source


def search_xiao_bao(query: str) -> [Show]:
    search_url: str = "https://xiaoheimi.net/index.php/vod/search.html?wd=" + query + "&submit="
    search_result_page: bytes = requests.get(search_url,
                                             headers={
                                                 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36' }).content
    query_result_soup: BeautifulSoup = BeautifulSoup(search_result_page, 'html.parser')
    query_results: ResultSet[Any] = query_result_soup.find_all('li', attrs={ 'class': 'clearfix' })
    result_list = []
    result_index: int = 1

    for result in query_results:
        show = Show(result, Source.XiaoBao)
        result_list.append(show)
    return result_list

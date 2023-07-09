from typing import Any, re

import cloudscraper
from bs4 import BeautifulSoup, ResultSet

from Show import Show, Source


def search_mov(query: str):
    search_url: str = f"https://ww1.new-movies123.co/search/{query}"
    scraper = cloudscraper.create_scraper(delay=10, browser={ 'custom': 'ScraperBot/1.0', })
    search_result_page = scraper.get(search_url).content
    query_result_soup: BeautifulSoup = BeautifulSoup(search_result_page, 'html.parser')
    query_results: ResultSet[Any] = query_result_soup.find_all('a', attrs={ 'class': 'item_series' })
    result_list = []
    result_index: int = 1

    for result in query_results:
        show = MOV.from_query(result)
        result_list.append(show)
    return result_list


class MOV(Show):
    def __init__(self, result):
        super().__init__(Source.MOV, result)

    @classmethod
    def from_json(cls, json_content):
        return cls(json_content)

    @classmethod
    def from_query(cls, query_result):
        data = {
            'title': query_result['title'],
            'note': None,
            'source_id': None,
            'details_url': f'https://ww1.new-movies123.co{query_result["href"]}'
        }

        return cls(data)

    def fetch_details(self):
        soup = super().fetch_details_soup()

        self.details['title'] = self.title
        self.details['episodes'] = soup.find("div", attrs={ "aria-labelledby": "episodes-select-tab" }).find_all('a')
        self.details['year'] = soup.find('a', { 'href': re.compile(r'/year/[0-9]{4}') }).get_text()
        print(self.details['episodes'])
        print(self.details['year'])
        # BUG: Can't find link to good quality video
        return self.details

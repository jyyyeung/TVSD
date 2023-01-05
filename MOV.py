from typing import Any

import cloudscraper
from bs4 import BeautifulSoup, ResultSet

from Show import Show, Source


def search_mov(self, query: str):
    search_url: str = f"https://ww1.new-movies123.co/search/{query}"
    scraper = cloudscraper.create_scraper(delay=10, browser={ 'custom': 'ScraperBot/1.0', })
    search_result_page = scraper.get(search_url).content
    query_result_soup: BeautifulSoup = BeautifulSoup(search_result_page, 'html.parser')
    query_results: ResultSet[Any] = query_result_soup.find_all('a', attrs={ 'class': 'item_series' })
    result_list = []
    result_index: int = 1

    for result in query_results:
        show = MOV(result)
        result_list.append(show)
    return result_list


class MOV(Show):
    def __init__(self, result):
        super().__init__(result, Source.MOV)
        self.title = result['title']
        self.note = ""
        self.source_id = ""
        self.details_url = f'https://ww1.new-movies123.co{result["href"]}'

    def fetch_details(self):
        soup = super().fetch_details_soup()

        self.details['title'] = self.title
        self.details['episodes'] = soup.find("div", attrs={ "aria-labelledby": "episodes-select-tab" }).find_all('a')
        self.details['year'] = soup.find('a', { 'href': re.compile(r'/year/[0-9]{4}') }).get_text()
        print(self.details['episodes'])
        print(self.details['year'])
        # BUG: Can't find link to good quality video

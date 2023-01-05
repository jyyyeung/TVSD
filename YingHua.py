from typing import Any

import cloudscraper
from bs4 import BeautifulSoup, ResultSet
from urllib.parse import unquote

from Show import Show, Source


def search_yinghua(query: str) -> [Show]:
    search_url: str = f"https://www.yhdmp.cc/s_all?ex=1&kw={query}"
    scraper = cloudscraper.create_scraper(delay=10, browser={ 'custom': 'ScraperBot/1.0', })
    search_result_page = scraper.get(search_url).content
    query_result_soup: BeautifulSoup = BeautifulSoup(search_result_page, 'html.parser')
    try:
        query_results: ResultSet[Any] = query_result_soup.find('div', attrs={ 'class': 'lpic' }).findChildren('li')
        result_index: int = 1
        result_list = []
    except AttributeError:
        return []

    for result in query_results:
        show = YingHua(result)
        result_list.append(show)
    return result_list


class YingHua(Show):
    def __init__(self, result, source: Source):
        super().__init__(result, Source.YingHua)

        self.title = result.find_all('a')[1].get_text()
        self.note = result.find('font').get_text()
        self.source_id = ''
        self.details_url = f'https://www.yhdmp.cc{result.find("a")["href"]}'

    def fetch_details(self):
        soup = super().fetch_details_soup()

        self.details['title'] = self.title
        self.details['episodes'] = soup.find_all('div', attrs={ "class": 'movurl' })[1].findChildren('a')
        self.details['year'] = soup.find('a', { 'href': re.compile(r'/list/\?year=[0-9]{4}') }).get_text()

    def fetch_episode_m3u8(self, episode_url):
        episode_details_page = self._scraper.get(f'https://www.yhdmp.cc{episode_url}').content
        episode_soup: BeautifulSoup = BeautifulSoup(episode_details_page, 'html.parser')
        source_str = episode_soup.find('iframe', attrs={ 'id': 'yh_playfram' })['src']
        if len(source_str) == 0:
            print("No Source available...")
            return
        episode_m3u8: str = f"{episode_soup.find('iframe', attrs={ 'id': 'yh_playfram' })['src'].split('.m3u8')[0].split('url=')[1]}.m3u8"
        episode_m3u8 = unquote(episode_m3u8)
        return episode_m3u8

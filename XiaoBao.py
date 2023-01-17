import re
from typing import Any

import cloudscraper
from bs4 import BeautifulSoup, ResultSet

from Show import Show, Source


def search_xiaobao(query):
    """

    :param query:
    :type query:
    :return:
    :rtype: 
    """
    search_url: str = "https://xiaoheimi.net/index.php/vod/search.html?wd=" + query + "&submit="
    scraper = cloudscraper.create_scraper(delay=10, browser={ 'custom': 'ScraperBot/1.0', })
    search_result_page = scraper.get(search_url).content

    query_result_soup: BeautifulSoup = BeautifulSoup(search_result_page, 'html.parser')
    query_results: ResultSet[Any] = query_result_soup.find_all('li', attrs={ 'class': 'clearfix' })
    result_list = []
    result_index: int = 1
 
    for result in query_results:
        show = XiaoBao.from_query(result)
        result_list.append(show)
    return result_list


class XiaoBao(Show):
    """

    """

    def __init__(self, result):
        super().__init__(Source.XiaoBao, result)

    @classmethod
    def from_json(cls, json_content):
        return cls(json_content)

    @classmethod
    def from_query(cls, query_result):
        show = query_result.find('a', attrs={ 'class': 'myui-vodlist__thumb' })['href']

        data = {
            'title': query_result.find('a', attrs={ 'class': 'searchkey' }).get_text(),
            'note': query_result.find('span', attrs={ 'class': 'pic-text text-right' }).get_text(),
            'source_id': re.search(r'/index.php/vod/detail/id/(\d+).html', show).group(1),
            'details_url': "https://xiaoheimi.net/index.php/vod/detail/id/" + super().source_id + ".html"
        }

        return cls(data)

    def fetch_details(self):
        soup = super().fetch_details_soup()

        print(soup.title.string)

        self.details['title']: str = str(soup.title.string).replace(" - 小宝影院 - 在线视频", "")
        self.details['description'] = soup.find("span", attrs={ "class": "data", "style": "display: none;" }).get_text()
        self.details['episodes'] = soup.find("ul", attrs={ 'class': "myui-content__list" }).contents
        self.details['year'] = str(soup.find("p", attrs={ "class": "data" }).contents[-1].get_text())

        return self.details

    def fetch_episode_m3u8(self, episode_url):
        episode_details_page = self._scraper.get('https://xiaoheimi.net' + episode_url).content
        episode_soup: BeautifulSoup = BeautifulSoup(episode_details_page, 'html.parser')
        episode_script: str = str(episode_soup.find('div', attrs={ "class": "myui-player__box" }).find('script'))
        episode_m3u8 = re.findall(r"https:\\\/\\\/m3u.haiwaikan.com\\\/xm3u8\\\/[\w\d]+.m3u8", episode_script)[
            0].replace(
            '\\', "")
        return episode_m3u8

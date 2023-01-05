import re
from typing import Any

from bs4 import BeautifulSoup, ResultSet

from Show import Show, Source
import cloudscraper


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
        show = XiaoBao(result)
        result_list.append(show)
    return result_list


class XiaoBao(Show):
    """

    """

    def __init__(self, result):
        super().__init__(result, Source.XiaoBao)

        self.title = result.find('a', attrs={ 'class': 'searchkey' }).get_text()
        self.note = result.find('span', attrs={ 'class': 'pic-text text-right' }).get_text()
        show = result.find('a', attrs={ 'class': 'myui-vodlist__thumb' })['href']
        self.source_id = re.search(r'/index.php/vod/detail/id/(\d+).html', show).group(1)
        show_details_url: [str, Any] = "https://xiaoheimi.net/index.php/vod/detail/id/" + self.source_id + ".html"
        self._details_url = show_details_url

    def fetch_details(self):
        soup = super().fetch_details_soup()

        self.details['title']: str = str(soup.title.string).replace(" - 小宝影院 - 在线视频", "")
        self.details['description'] = soup.find("span", attrs={ "class": "data", "style": "display: none;" }).get_text()
        self.details['episodes'] = soup.find("ul", attrs={ 'class': "myui-content__list" }).contents
        self.details['year'] = str(soup.find("p", attrs={ "class": "data" }).contents[-1].get_text())

    def fetch_episode_m3u8(self, episode_url):
        episode_details_page = self._scraper.get('https://xiaoheimi.net' + episode_url).content
        episode_soup: BeautifulSoup = BeautifulSoup(episode_details_page, 'html.parser')
        episode_script: str = str(episode_soup.find('div', attrs={ "class": "myui-player__box" }).find('script'))
        episode_m3u8 = re.findall(r"https:\\\/\\\/m3u.haiwaikan.com\\\/xm3u8\\\/[\w\d]+.m3u8", episode_script)[
            0].replace(
            '\\', "")
        return episode_m3u8

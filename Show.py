import re
from enum import Enum
from typing import Any, Union

import cloudscraper
import requests
from bs4 import BeautifulSoup

from fake_useragent import UserAgent

ua = UserAgent()


class Source(Enum):
    XiaoBao = 1
    OVLED = 2
    MOV = 3
    YingHua = 4
    OLEVOD = 5


class Show:
    def __init__(self, result, source: Source):
        self._source = source
        if source == Source.XiaoBao:
            self.title = result.find('a', attrs={ 'class': 'searchkey' }).get_text()
            self.note = result.find('span', attrs={ 'class': 'pic-text text-right' }).get_text()
            show = result.find('a', attrs={ 'class': 'myui-vodlist__thumb' })[
                'href']
            self.source_id = re.search(r'/index.php/vod/detail/id/(\d+).html', show).group(1)
            show_details_url: Union[
                str, Any] = "https://xiaoheimi.net/index.php/vod/detail/id/" + self.source_id + ".html"
            self._details_url = show_details_url
        elif source == Source.MOV:
            self.title = result['title']
            self.note = ""
            self.source_id = ""
            self.details_url = f'https://ww1.new-movies123.co{result["href"]}'
        elif source == Source.YingHua:
            self.title = result.find_all('a')[1].get_text()
            self.note = result.find('font').get_text()
            self.source_id = ''
            self.details_url = f'https://www.yhdmp.cc{result.find("a")["href"]}'
        elif source == Source.OLEVOD:
            self.title = result.find('a', attrs={ 'class': 'vodlist_thumb' })['title']
            self.note = result.find('span', attrs={ 'class': 'pic_text text_right' }).get_text()
            show = result.find('a', attrs={ 'class': 'vodlist_thumb' })[
                'href']
            self.source_id = re.search(r'/index.php/vod/detail/id/(\d+).html', show).group(1)
            show_details_url: Union[
                str, Any] = "https://www.olevod.com/index.php/vod/detail/id/" + self.source_id + ".html"
            self._details_url = show_details_url
        print(self.source_id)
        print(self._details_url)

    @property
    def title(self):  # This getter method name is *the* name
        return self._title

    @title.setter  # the property decorates with `.setter` now
    def title(self, title):  # name, e.g. "attribute", is the same
        self._title = title  # the "value" name isn't special

    @property
    def note(self):  # This getter method name is *the* name
        return self._note

    @note.setter  # the property decorates with `.setter` now
    def note(self, note):  # name, e.g. "attribute", is the same
        self._note = note  # the "value" name isn't special

    @property
    def source_id(self):  # This getter method name is *the* name
        return self._source_id

    @source_id.setter  # the property decorates with `.setter` now
    def source_id(self, source_id):  # name, e.g. "attribute", is the same
        self._source_id = source_id  # the "value" name isn't special

    @property
    def details_url(self):  # This getter method name is *the* name
        return self._details_url

    @details_url.setter  # the property decorates with `.setter` now
    def details_url(self, details_url):  # name, e.g. "attribute", is the same
        self._details_url = details_url  # the "value" name isn't special

    def fetch_details(self):
        # show_details_page: bytes = requests.get(url=self.details_url, headers={ 'User-Agent': ua.random }).content
        scraper = cloudscraper.create_scraper(delay=10, browser={ 'custom': 'ScraperBot/1.0', })
        show_details_page = scraper.get(self.details_url).content
        # soup: BeautifulSoup = BeautifulSoup(show_details_page, 'html.parser')
        soup: BeautifulSoup = BeautifulSoup(show_details_page, 'html.parser')

        details = { 'title': None, 'description': None, 'episodes': [None], 'year': None }
        if self._source == Source.XiaoBao:
            details['title']: str = str(soup.title.string).replace(" - 小宝影院 - 在线视频", "")
            details['description'] = soup.find("span", attrs={ "class": "data", "style": "display: none;" }).get_text()
            details['episodes'] = soup.find("ul", attrs={ 'class': "myui-content__list" }).contents
            details['year'] = str(soup.find("p", attrs={ "class": "data" }).contents[-1].get_text())
        elif self._source == Source.MOV:
            details['title'] = self.title
            details['episodes'] = soup.find("div", attrs={ "aria-labelledby": "episodes-select-tab" }).find_all('a')
            details['year'] = soup.find('a', { 'href': re.compile(r'/year/[0-9]{4}') }).get_text()
            print(details['episodes'])
            print(details['year'])
            # BUG: Can't find link to good quality video
            # TODO: Use VPN
        elif self._source == Source.YingHua:
            details['title'] = self.title
            details['episodes'] = soup.find_all('div', attrs={ "class": 'movurl' })[1].findChildren('a')
            details['year'] = soup.find('a', { 'href': re.compile(r'/list/\?year=[0-9]{4}') }).get_text()
        elif self._source == Source.OLEVOD:
            details['title']: str = soup.find("h2", attrs={ "class": "title" }).get_text()
            details['description'] = soup.find("div", attrs={ "class": "content_desc" }).find("span").get_text()
            details['episodes'] = soup.find("ul", attrs={ 'class': "content_playlist" }).find_all("li")
            details['year'] = soup.find('a',
                                        { 'href': re.compile(r'/index.php/vod/search/year/[0-9]{4}.html') }).get_text()
        return details

    @property
    def source(self):  # This getter method name is *the* name
        return self._source

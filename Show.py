import re
from enum import Enum
from typing import Any

import requests
from bs4 import BeautifulSoup


class Source(Enum):
    XiaoBao = 1
    OVLED = 2
    MOV = 3


class Show:
    def __init__(self, result, source: Source):
        if source == Source.XiaoBao:
            self._source = source
            self.title = result.find('a', attrs={'class': 'searchkey'}).get_text()
            self.note = result.find('span', attrs={'class': 'pic-text text-right'}).get_text()
            show = result.find('a', attrs={'class': 'myui-vodlist__thumb'})[
                'href']
            self.source_id = re.search(r'/index.php/vod/detail/id/(\d+).html', show).group(1)
            show_details_url: str | Any = "https://xiaoheimi.net/index.php/vod/detail/id/" + self.source_id + ".html"
            self._details_url = show_details_url

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
        show_details_page: bytes = requests.get(url=self.details_url, headers={'User-Agent': 'Mozilla/5.0'}).content
        soup: BeautifulSoup = BeautifulSoup(show_details_page, 'html.parser')

        details = {'title': None, 'description': None, 'episodes': [None], 'year': None}
        if self._source == Source.XiaoBao:
            details['title']: str = str(soup.title.string).replace(" - 小宝影院 - 在线视频", "")
            details['description'] = soup.find("span", attrs={"class": "data", "style": "display: none;"}).get_text()
            details['episodes'] = soup.find("ul", attrs={'class': "myui-content__list"}).contents
            details['year'] = str(soup.find("p", attrs={"class": "data"}).contents[-1].get_text())
        return details

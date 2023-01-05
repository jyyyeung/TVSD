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
    OLEVOD = 2
    MOV = 3
    YingHua = 4


class Show():
    """
    Contains a Show
    """

    def __init__(self, result, source: Source):
        self._source_id = None
        self._note = None
        self._title = None
        self._details_url = None
        self._source = source
        print(self.source_id)
        print(self._details_url)
        self.details = { 'title': None, 'description': None, 'episodes': [None], 'year': None }
        self._scraper = cloudscraper.create_scraper(delay=10, browser={ 'custom': 'ScraperBot/1.0', })

    @property
    def title(self):  # This getter method name is *the* name
        """

        :return:
        :rtype:
        """
        return self._title

    @title.setter  # the property decorates with `.setter` now
    def title(self, title):  # name, e.g. "attribute", is the same
        self._title = title  # the "value" name isn't special

    @property
    def note(self):  # This getter method name is *the* name
        """

        :return:
        :rtype:
        """
        return self._note

    @note.setter  # the property decorates with `.setter` now
    def note(self, note):  # name, e.g. "attribute", is the same
        self._note = note  # the "value" name isn't special

    @property
    def source_id(self):  # This getter method name is *the* name
        """

        :return:
        :rtype:
        """
        return self._source_id

    @source_id.setter  # the property decorates with `.setter` now
    def source_id(self, source_id):  # name, e.g. "attribute", is the same
        self._source_id = source_id  # the "value" name isn't special

    @property
    def details_url(self):  # This getter method name is *the* name
        """

        :return:
        :rtype:
        """
        return self._details_url

    @details_url.setter  # the property decorates with `.setter` now
    def details_url(self, details_url):  # name, e.g. "attribute", is the same
        self._details_url = details_url  # the "value" name isn't special

    def fetch_details(self):
        """

        :return:
        :rtype:
        """
        print("Method for finding details from this source is undefined...")
        return None

    def fetch_episode_m3u8(self, episode_url):
        """

        :return:
        :rtype:
        """
        print("Method for finding episode m3u8 from this source is undefined...")
        return None

    def fetch_details_soup(self):
        """

        :return: soup for details page
        :rtype: BeautifulSoup
        """
        show_details_page = self._scraper.get(self.details_url).content
        soup: BeautifulSoup = BeautifulSoup(show_details_page, 'html.parser')
        return soup

    @property
    def source(self):  # This getter method name is *the* name
        """

        :return: source of current Show
        :rtype: Source
        """
        return self._source

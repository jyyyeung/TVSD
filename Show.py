import json
from enum import Enum, auto

import cloudscraper
import typer
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ua = UserAgent()


def check_season_index(show_title: str) -> int:
    """
    Checks if season number for a particular show
    :param show_title:
    :type show_title:
    :return:
    :rtype:
    """
    if '第' in show_title:
        if '第一季' in show_title:
            return 1
        elif '第二季' in show_title:
            return 2
        elif '第三季' in show_title:
            return 3
        elif '第四季' in show_title:
            return 4
        elif '第五季' in show_title:
            return 5
        elif '第六季' in show_title:
            return 6
        elif '第七季' in show_title:
            return 7
        elif '第八季' in show_title:
            return 8
        elif '第九季' in show_title:
            return 9
    elif 'Season' in show_title:
        return int(show_title.lower().split('season')[-1])
    elif 'part' in show_title:
        return 1
    elif typer.prompt('这个节目是否续季？（not S1)', default='').capitalize() == 'Y':
        return typer.prompt(text='这个节目是第几季？', type=int)
    else:
        return 1


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class Source(AutoName):
    XiaoBao = auto()
    OLEVOD = auto()
    MOV = auto()
    YingHua = auto()
    BuDing3 = auto()


class Show:
    """
    Contains a Show
    """

    def __init__(self, source: Source, result=None):
        self._source_id = None
        self._note = None
        self._title = None
        self._details_url = None
        self._source = source
        self.details = {
            'title': None,
            'description': None,
            'episodes': [None],
            'year': None
        }
        self._scraper = cloudscraper.create_scraper(delay=10, browser={ 'custom': 'ScraperBot/1.0', })

        self._show_info = {
            "prefix": None,
            "begin_year": None,
            "season": None
        }

        if result is not None:
            print(result)
            self._title = result['title'] if 'title' in result.keys() else None
            self._note = result['note'] if 'note' in result.keys() else None
            self._source_id = result['source_id'] if 'source_id' in result.keys() else None
            self._details_url = result['details_url'] if 'details_url' in result.keys() else None
            if 'show_info' in result.keys(): self._show_info = result['show_info']
            # self._show_title = None

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

    def query_begin_year(self):
        details = self.fetch_details()
        show_year = int(details['year'])
        if self.show_season_index > 1:
            # TODO: Auto

            show_year = show_year - self.show_season_index + 1
            show_year = typer.prompt(text=f'第一季在那一年？(calculated={show_year})', type=int, default=show_year)
        self._show_info['year'] = show_year

        return show_year

    @property
    def show_begin_year(self):
        return self._show_info['begin_year'] if self._show_info['begin_year'] is not None else self.query_begin_year

    def query_season_index(self):
        season_index = check_season_index(self.title)
        season_index = typer.prompt(text='Fix the season index? ', default=season_index, type=int)
        self._show_info['season'] = season_index
        return season_index

    @property
    def show_season_index(self):
        print(self._show_info)
        return self._show_info['season'] if self._show_info['season'] is not None else self.query_season_index()

    def generate_prefix(self):
        show_details = self.fetch_details()

        show_title = show_details['title'].partition(" 第")[0]

        show_prefix: str = show_title + " (" + str(show_details['year']) + ")"
        self._show_info['prefix'] = show_prefix
        return show_prefix

    @property
    def show_prefix(self):
        return self._show_info['prefix'] if self._show_info['prefix'] is not None else self.generate_prefix()

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

    def save_source_details(self):
        show_details = {
            "title": self.title,
            "source": self.source,
            "details_url": self.details_url,
            "source_id": self.source_id,
            "note": self.note,
            "details": self.details
        }
        show_details_json = json.dumps(show_details, indent=4)
        with open("YYYDown_show.json", "w") as outfile:
            outfile.write(show_details_json)
        # print("This source has not been configured to save source details. ")

    @property
    def source(self):  # This getter method name is *the* name
        """

        :return: source of current Show
        :rtype: Source
        """
        return self._source

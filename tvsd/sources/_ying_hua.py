import re
from typing import Any
from urllib.parse import unquote

import cloudscraper
from bs4 import BeautifulSoup, ResultSet
from requests_html import HTMLSession
from Show import Show, Source


def search_yinghua(query: str) -> [Show]:
    search_url: str = f"https://www.yhdmp.cc/s_all?ex=1&kw={query}"
    scraper = cloudscraper.create_scraper(
        delay=10,
        browser={
            "custom": "ScraperBot/1.0",
        },
    )
    search_result_page = scraper.get(search_url).content
    query_result_soup: BeautifulSoup = BeautifulSoup(search_result_page, "html.parser")
    try:
        query_results: ResultSet[Any] = query_result_soup.find(
            "div", attrs={"class": "lpic"}
        ).findChildren("li")
        result_index: int = 1
        result_list = []
    except AttributeError:
        return []

    for result in query_results:
        show = YingHua.from_query(result)
        result_list.append(show)
    return result_list


class YingHua(Show):
    def __init__(self, result):
        super().__init__(Source.YingHua, result)

    @classmethod
    def from_json(cls, json_content):
        return cls(json_content)

    @classmethod
    def from_query(cls, query_result):
        data = {
            "title": query_result.find_all("a")[1].get_text(),
            "note": query_result.find("font").get_text(),
            "source_id": None,
            "details_url": f'https://www.yhdmp.cc{query_result.find("a")["href"]}',
        }

        return cls(data)

    def fetch_details(self):
        soup = super().fetch_details_soup()

        self.details["title"] = self.title
        self.details["episodes"] = soup.find_all("div", attrs={"class": "movurl"})[
            1
        ].findChildren("a")
        self.details["year"] = soup.find(
            "a", {"href": re.compile(r"/list/\?year=[0-9]{4}")}
        ).get_text()

        return self.details

    def fetch_episode_m3u8(self, episode_url):
        response = HTMLSession().get(f"https://www.yhdmp.cc{episode_url}")
        response.html.render(wait=2, sleep=3)

        source_str = (
            "https://www.yhdmp.cc" + response.html.find("iframe")[0].attrs["src"]
        )
        source_str = re.findall(r"https%3A.*m3u8", source_str)[0]

        if len(source_str) == 0:
            print("No Source available...")
            return
        episode_m3u8 = unquote(source_str)
        return episode_m3u8

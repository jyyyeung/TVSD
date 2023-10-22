import re
from typing import Any

import cloudscraper
from bs4 import BeautifulSoup, ResultSet
from Show import Show, Source


def search_iyf(query: str) -> [Show]:
    """

    :param query:
    :type query:
    :return:
    :rtype:
    """
    search_url: str = f"https://rankv21.iyf.tv/v3/list/briefsearch?tags={query}&orderby=4&page=1&size=36&desc=1&isserial=-1"
    scraper = cloudscraper.create_scraper(
        delay=10,
        browser={
            "custom": "ScraperBot/1.0",
        },
    )
    search_result_page = scraper.get(search_url).content
    query_result_soup: BeautifulSoup = BeautifulSoup(search_result_page, "html.parser")
    query_results: ResultSet[Any] = query_result_soup.find_all(
        "li", attrs={"class": "searchlist_item"}
    )
    result_list = []
    result_index: int = 1

    for result in query_results:
        show = IYF.from_query(result)
        result_list.append(show)
    return result_list


class IYF(Show):
    def __init__(self, result):
        super().__init__(Source.OLEVOD, result)

    @classmethod
    def from_json(cls, json_content):
        return cls(json_content)

    @classmethod
    def from_query(cls, query_result):
        try:
            note = query_result.find(
                "span", attrs={"class": "pic_text text_right"}
            ).get_text()
        except AttributeError:
            note = ""

        show = query_result.find("a", attrs={"class": "vodlist_thumb"})["href"]
        source_id = re.search(r"/index.php/vod/detail/id/(\d+).html", show).group(1)

        data = {
            "title": query_result.find("a", attrs={"class": "vodlist_thumb"})["title"],
            "note": note,
            "source_id": source_id,
            "details_url": f"https://www.olevod.com/index.php/vod/detail/id/{source_id}.html",
        }

        return cls(data)

    def fetch_details(self):
        """ """
        soup = super().fetch_details_soup()

        self.details["title"]: str = soup.find(
            "h2", attrs={"class": "title"}
        ).get_text()
        self.details["description"] = (
            soup.find("div", attrs={"class": "content_desc"}).find("span").get_text()
        )
        self.details["episodes"] = soup.find(
            "ul", attrs={"class": "content_playlist"}
        ).find_all("li")
        self.details["year"] = soup.find(
            "a", {"href": re.compile(r"/index.php/vod/search/year/[0-9]{4}.html")}
        ).get_text()

        return self.details

    def fetch_episode_m3u8(self, episode_url):
        episode_details_page = self._scraper.get(
            "https://www.olevod.com" + episode_url
        ).content
        episode_soup: BeautifulSoup = BeautifulSoup(episode_details_page, "html.parser")
        episode_script: str = str(
            episode_soup.find("div", attrs={"class": "player_video"}).find("script")
        )
        episode_m3u8 = re.findall(
            r"https:\\\/\\\/europe.olemovienews.com[\w\d\/\\\.]*.m3u8", episode_script
        )[0].replace("\\", "")
        return episode_m3u8

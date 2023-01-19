import re
import urllib.parse

import requests
from requests_html import HTMLSession

from Show import Show, Source


def search_bu_ding3(query):
    """

    :param query:
    :type query:
    :return:
    :rtype: 
    """
    print(urllib.parse.quote(query))
    if len(urllib.parse.quote(query)) > 30:
        return None
    search_url: str = f"https://s5.quelingfei.com:4438/ssszz.php"
    request = requests.get(search_url, params={
        "q": query,
        "top": 10,
        "dest": 0
    })
    # f = urllib.request.urlopen(search_url)
    # query_results = zlib.decompress(f.read(), 16 + zlib.MAX_WBITS)
    request.raise_for_status()
    query_results = res = list(eval(str(request.content, 'utf-8-sig')))
    print(query_results)
    result_list = []
    result_index: int = 1

    for result in query_results:
        show = BuDing3.from_query(result)
        result_list.append(show)
    return result_list


class BuDing3(Show):
    """

    """

    def __init__(self, result):
        super().__init__(Source.BuDing3, result)

    @classmethod
    def from_json(cls, json_content):
        return cls(json_content)

    @classmethod
    def from_query(cls, query_result):
        data = {
            'title': query_result['title'],
            'note': None,
            'source_id': None,
            'details_url': 'https://buding3.com' + query_result['url'],
            'year': query_result['time']
        }

        return cls(data)

    def fetch_details(self):
        soup = super().fetch_details_soup()

        self.details['title']: str = soup.find("img", attrs={ "class": "lazy" })['alt']
        self.details['description'] = soup.find("div", attrs={ "class": "des2" }).get_text()
        self.details['episodes'] = soup.find("ul", attrs={ 'id': "ul_playlist_1" }).contents
        self.details['year'] = soup.find({ 'dd': re.compile(r'<b>年代：</b>\n[0-9]{4}') }).get_text().split('</b>')[
            -1]

        print(self.details['year'])

        return self.details

    def fetch_episode_m3u8(self, episode_url):
        response = HTMLSession().get(f'https://buding3.com{episode_url}')
        print(f'https://buding3.com{episode_url}')
        # BUG: Request timeout
        response.html.render(wait=2, sleep=3)

        source_str = 'https://www.yhdmp.cc' + response.html.find('iframe')['src']
        print(source_str)
        # source_str = re.findall(r'https%3A.*m3u8', source_str)[0]

        if len(source_str) == 0:
            print("No Source available...")
            return
        episode_m3u8 = source_str

        return episode_m3u8

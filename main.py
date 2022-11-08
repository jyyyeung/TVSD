# -*- coding: utf-8 -*-
import os.path
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
import m3u8_To_MP4

query = urllib.parse.quote(input("请输入节目名字："))

search_url = "https://xiaoheimi.net/index.php/vod/search.html?wd=" + query + "&submit="
search_result_page = requests.get(search_url,
                                  headers={ 'User-Agent': 'Mozilla/5.0' }).content
query_result_soup = BeautifulSoup(search_result_page, 'html.parser')
query_results = query_result_soup.find_all('li', attrs={ 'class': 'clearfix' })

result_index = 1
for result in query_results:
    result_name = result.find('a', attrs={ 'class': 'searchkey' }).get_text()
    note = result.find('span', attrs={ 'class': 'pic-text text-right' }).get_text()
    print(result_index, result_name, note)
    result_index += 1

chosen_show = query_results[int(input("请选择你下载的节目：")) - 1].find('a', attrs={ 'class': 'myui-vodlist__thumb' })[
    'href']
show_index = re.search('/index.php/vod/detail/id/(\d+).html', chosen_show).group(1)

show_details_url = "https://xiaoheimi.net/index.php/vod/detail/id/" + show_index + ".html"
show_details_page = requests.get(url=show_details_url, headers={ 'User-Agent': 'Mozilla/5.0' }).content

soup = BeautifulSoup(show_details_page, 'html.parser')

show_title = str(soup.title.string).replace(" - 小宝影院 - 在线视频", "")
show_description = soup.find("span", attrs={ "class": "data", "style": "display: none;" }).get_text()
show_episodes = soup.find("ul", attrs={ 'class': "myui-content__list" }).contents
show_year = str(soup.find("p", attrs={ "class": "data" }).contents[-1].get_text())

season_index = 1

if '第' in show_title or input('这个节目是否续季？（not S1)').capitalize() == 'Y':
    season_index = int(input('这个节目是第几季？'))
    # TODO: Auto
    show_year = int(input('第一季在那一年？'))
    # TODO: Auto?
    show_title = input(show_title + '的 general 节目名称是：')

show_prefix = show_title + " (" + str(show_year) + ")"

base_path = '/Volumes/Viewable'
show_dir = base_path + '/TV Series/' + show_prefix
if os.path.ismount(base_path):
    if not os.path.isdir(show_dir):
        os.mkdir(show_dir)
    show_dir = show_dir + "/Season " + str(season_index).zfill(2)
    if not os.path.isdir(show_dir):
        os.mkdir(show_dir)
else:
    print(base_path, "has not been mounted yet. Exiting...")
    quit()

download_all = str(input('Would you like to download all episodes? (Y/n)')).capitalize() == 'Y'


def download_episode(episode):
    """
    Downloads episode
    :param episode: BeautifulSoup Episode Object
    :type episode:
    :return: void
    :rtype:
    """
    episode_name = episode["title"]
    episode_url = episode.a['href']
    episode_filename = show_prefix + " - S" + str(season_index).zfill(2) + "E" + str(episode_index).zfill(
        2) + " - " + episode_name
    if os.path.isfile(show_dir + '/' + episode_filename):
        return
    print(episode_name, episode_url)
    episode_details_page = requests.get(url='https://xiaoheimi.net' + episode_url,
                                        headers={ 'User-Agent': 'Mozilla/5.0' }).content
    episode_soup = BeautifulSoup(episode_details_page, 'html.parser')
    episode_script = str(episode_soup.find('div', attrs={ "class": "myui-player__box" }).find('script'))
    episode_m3u8 = re.findall("https:\\\/\\\/m3u.haiwaikan.com\\\/xm3u8\\\/[\w\d]+.m3u8", episode_script)[0].replace(
        '\\', "")

    # TODO: Background download
    if download_all or str(
            input('Would you like to download this episode? (Y/n)')).capitalize() == 'Y':
        m3u8_To_MP4.multithread_uri_download(m3u8_uri=episode_m3u8,
                                             mp4_file_name=episode_filename, mp4_file_dir=show_dir)
        print("成功下载", episode_name)


episode_index = 1
for episode in show_episodes:
    download_episode(episode)
    episode_index += 1

print(show_title, "下载完成")

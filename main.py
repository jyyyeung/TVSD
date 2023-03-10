# -*- coding: utf-8 -*-
import os.path
import re
import shutil
from difflib import SequenceMatcher
from typing import Any, Union

import m3u8_To_MP4
import typer
from bs4 import PageElement

import OLEVOD
import Show
import XiaoBao
import utils

# import tvdb_v4_official

app = typer.Typer()

global db


# Login to TVDB
# tvdb = tvdb_v4_official.TVDB("afb01b0b-7823-4d53-92b5-078fbd649c49")


# def search_tvdb():
#


def search_media(query):
    """

    :param query:
    :type query:
    """
    # parser.add_argument("media_name", type=str, help="Name of Media to download")
    # args = parser.parse_args()
    # print(args)

    # query: str = urllib.parse.quote(input("请输入节目名字："))
    # query: str = args.media_name
    print(query)

    chosen_show = None
    is_exist = False

    # dir loop check dir
    for directory in os.listdir(base_path + '/TV Series/'):
        season_title = directory.split(' ')[0]
        similarity_ratio = SequenceMatcher(None, query, season_title).ratio()
        if similarity_ratio >= 0.8:
            # print(season_title, similarity_ratio)
            if typer.prompt(text=f'Are you looking for {directory}?', type=str, default='n').capitalize() == 'Y':
                is_exist = True
                chosen_show = utils.load_source_details(base_path + '/TV Series/' + directory)

    if not is_exist or chosen_show is None:
        # SequenceMatcher(None, a, b).ratio()

        result: Union[PageElement, Any]
        # for result in query_results:
        #     result_index += 1

        query_results: [Show] = []
        # TODO: Search in db first / or put db results first
        # query_results += BuDing3.search_bu_ding3(query)
        query_results += XiaoBao.search_xiaobao(query)
        # query_results += MOV.search_mov(query)
        # query_results += YingHua.search_yinghua(query)
        query_results += OLEVOD.search_olevod(query)

        for result_index, result in enumerate(query_results):
            # print(result.title)
            print(result_index, result.source, result.title, result.note)

        chosen_show = query_results[typer.prompt(text='请选择你下载的节目', type=int)]

    # TODO: if searched result is from database, get source from db
    show_details = chosen_show.fetch_details()

    show_title = chosen_show.title

    print(chosen_show)

    # TODO: if from db, fetch season_index from db if possible
    season_index = chosen_show.show_season_index

    # TODO: if from db, fetch year of first season if possible
    # print(season_index)
    show_year = chosen_show.show_begin_year

    # TODO: Check
    # show_title = typer.prompt(show_title + '的 general 节目名称是：')
    # TODO: if from db, fetch general title, or directory name from database
    show_prefix = chosen_show.show_prefix

    # TODO: Check if directory for this show exists, if so, get that directory
    show_dir: str = base_path + '/TV Series/' + show_prefix
    utils.mkdir_if_no(show_dir)

    # TODO: Check monitor file in directory, check files not downloaded
    # IDEA: it is known that hash is unique for a video, if so, hash can be matched to ensure there are no additional ads embedded in videos
    download_all: bool = typer.prompt(text='Would you like to download all episodes? (Y/n)',
                                      type=str, default='Y').capitalize() == 'Y'

    episode_index: int = 0

    specials_index: int = utils.get_next_specials_index(show_dir)
    print(specials_index)

    for episode in show_details['episodes']:
        try:
            episode_name = episode["title"]
        except KeyError:
            episode_name = episode.find('a').get_text()
        episode_number = None
        if download_all or typer.prompt(text=f'Would you like to download this {episode_name}? (Y/n)',
                                        type=str, default='n').capitalize() == 'Y':
            not_specials = re.match(
                r"^[0-9]{8}$|^[0-9]{8}[（(]*第([0-9]+)[期集][(（上中下)）]*[)）]?$|^([0-9]{1,3})$|^第([0-9]+)[期集][上中下]*$",
                episode_name)
            if not_specials:
                season_dir = show_dir + "/Season " + str(season_index).zfill(2)
                episode_index += 1
                try:
                    episode_number = re.search(
                        r"^[0-9]{8}[（(]*第(\d+)[期集][(（上中下)）]*[)）]?$|^(\d{1,3})$|^第(\d+)[期集][上中下]*$",
                        episode_name).groups()[0]
                    # print(episode_number)
                    episode_index = int(re.findall(r'\d+', episode_number)[0])

                    # print(episode_number)

                except AttributeError:
                    episode_number = episode_index

            else:
                print("Episode should be Specials")
                season_dir = show_dir + "/Specials"
                # download_episode(show_prefix, season_dir, episode_index, episode)
                specials_index += 1

            utils.mkdir_if_no(season_dir)

            download_episode(show_prefix, season_index if not_specials else 0, season_dir,
                             episode_index if not_specials else specials_index, episode,
                             chosen_show)
    chosen_show.save_source_details()
    print(show_title, " 下载完成")


def download_episode(show_prefix: str, season_index: int, season_dir: str, episode_index: int, episode, show):
    """
        Downloads episode
        :param season_index:
        :type season_index:
        :param show_prefix:
        :type show_prefix:
        :param season_dir: Directory path storing the episodes from this season
        :type season_dir: str
        :param episode_index: Episode Number
        :type episode_index: int
        :param episode: BeautifulSoup Episode Object
        :type episode:
        :return: void
        :rtype:
        """

    try:
        episode_name = episode["title"]
    except KeyError:
        episode_name = episode.find('a').get_text()

    if episode.find('a') is None:
        episode_url = episode['href']
    else:
        episode_url = episode.find('a')['href']
    episode_filename: Union[
        str, Any] = f"{show_prefix} - S{str(season_index).zfill(2)}E{str(episode_index).zfill(2)} - {episode_name}"

    # Check if file exists already
    if os.path.isfile(f"{season_dir}/{episode_filename}.mp4"):
        print(f"{episode_filename} already exists in directory, skipping... ")
        return
    # specials exists already
    for existing_episode in os.listdir(season_dir):
        # print(episode_name, existing_episode)
        if existing_episode.endswith(".mp4") and episode_name in existing_episode:
            print(f"{episode_filename} probably exist as {existing_episode}, skipping...")
            return

    print(f"Downloading to file {episode_filename}")

    # print(episode_name, episode_url)
    episode_m3u8 = ''
    episode_m3u8 = show.fetch_episode_m3u8(episode_url)
    print(episode_m3u8)

    # TODO: Background download

    # m3u8_To_MP4.multithread_uri_download(m3u8_uri=episode_m3u8,
    # mp4_file_name=episode_filename, mp4_file_dir=show_dir)
    if 'm3u8' not in episode_m3u8:
        print('m3u8 Load Error, Stream probably does not exist: ' + episode_m3u8)
        return
    temp_dir = '/Users/yyymx/Movies/temp-parts/' + episode_filename
    if not os.path.isdir(temp_dir):
        os.mkdir(temp_dir)
        m3u8_To_MP4.multithread_uri_download(m3u8_uri=episode_m3u8,
                                             mp4_file_name=episode_filename, mp4_file_dir=season_dir,
                                             tmpdir=temp_dir)
        print('Completed downloading, removing temp dir...')
        # os.rmdir(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
    else:
        print('Temp Dir for this episode exists, should be already downloading')

    # print("成功下载", episode_name)


def check_dir_mounted(path: str):
    """
    Check if a directory exists
    :param path: Path to check
    :type path: str
    """
    if not os.path.ismount(path):
        print(path, "has not been mounted yet. Exiting...")
        quit()


if __name__ == '__main__':
    # app()
    base_path: str = '/Volumes/Viewable'
    check_dir_mounted(base_path)
    # db = fetch_db()
    typer.run(search_media)

import json
import os
import re

from MOV import MOV
from OLEVOD import OLEVOD
from Show import Source
from XiaoBao import XiaoBao
from YingHua import YingHua


def load_source_details(season_dir: str):
    # print(season_dir)
    dir_file = os.path.join(season_dir, 'YYYDown_show.json')
    if not os.path.isfile(dir_file):
        return None
    show_details = json.load(open(dir_file, 'r'))
    # print(show_details)
    source = Source(show_details['source'])

    if source == Source.XiaoBao:
        return XiaoBao.from_json(show_details)
    if source == Source.MOV:
        return MOV.from_json(show_details)
    if source == Source.YingHua:
        return YingHua.from_json(show_details)
    if source == Source.OLEVOD:
        return OLEVOD.from_json(show_details)


def mkdir_if_no(check_dir: str):
    if not os.path.isdir(check_dir):
        os.mkdir(check_dir)


def get_next_specials_index(show_dir: str) -> int:
    existing_episode_indexes: [int] = []
    specials_dir = show_dir + "/Specials"
    if os.path.exists(specials_dir):
        for existing_special in os.listdir(specials_dir):
            try:
                existing_episode_indexes += re.search(r'S00E(\d{2})', existing_special).groups()
            except AttributeError:
                print("No Existing Specials")
        existing_episode_indexes.sort()
        if len(existing_episode_indexes) > 0:
            return int(existing_episode_indexes[-1])
    return 0

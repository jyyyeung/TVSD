import json
import os

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

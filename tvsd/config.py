"""This module provides the RP To-Do config functionality."""
# rptodo/config.py

import configparser
from ctypes.wintypes import SERVICE_STATUS_HANDLE
import os
from pathlib import Path
from re import T


import typer

from tvsd import DB_WRITE_ERROR, DIR_ERROR, FILE_ERROR, SUCCESS, __app_name__

config_parser = configparser.ConfigParser()

CONFIG_DIR_PATH = Path(typer.get_app_dir(__app_name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"


class Config:
    def __init__(self):
        config_parser.read(CONFIG_FILE_PATH)

    @classmethod
    def init_app(cls, db_path: str) -> int:
        """Initialize the application."""
        config_code = cls._init_config_file()
        if config_code != SUCCESS:
            return config_code
        database_code = cls._create_database(db_path)
        if database_code != SUCCESS:
            return database_code
        return SUCCESS

    @classmethod
    def _init_config_file(cls) -> int:
        try:
            CONFIG_DIR_PATH.mkdir(exist_ok=True)
        except OSError:
            return DIR_ERROR
        try:
            CONFIG_FILE_PATH.touch(exist_ok=True)
        except OSError:
            return FILE_ERROR
        return SUCCESS

    def validate_config_file(self) -> None:
        if not os.path.exists(CONFIG_FILE_PATH):
            self._init_config_file()
        if not config_parser.has_section("General"):
            config_parser["General"] = {
                "base_path": "/Volumes/Viewable",
                "temp_base_path": "~/Movies/temp-parts",
                "series_dir": "TV Series",
                "specials_dir": "Specials",
            }

    @classmethod
    def _create_database(cls, db_path: str) -> int:
        # config_parser = configparser.ConfigParser()
        config_parser["General"] = {"database": db_path}
        try:
            with CONFIG_FILE_PATH.open("w") as file:
                config_parser.write(file)
        except OSError:
            return DB_WRITE_ERROR
        return SUCCESS

    @property
    def temp_base_path(self) -> str:
        try:
            self.validate_config_file()
            return config_parser["General"]["temp_base_path"]
        except KeyError:
            return "~/Movies/temp-parts"

    @property
    def base_path(self) -> str:
        try:
            self.validate_config_file()
            return config_parser["General"]["base_path"]
        except KeyError:
            return "/Volumes/Viewable"

    @property
    def series_dir(self) -> str:
        try:
            self.validate_config_file()
            return config_parser["General"]["series_dir"]
        except KeyError:
            return "TV Series"

    @property
    def specials_dir(self) -> str:
        try:
            self.validate_config_file()
            return config_parser["General"]["specials_dir"]
        except KeyError:
            return "Specials"


config = Config()
BASE_PATH = config.base_path
TEMP_BASE_PATH = config.temp_base_path
validate_config_file = config.validate_config_file
SERIES_DIR = config.series_dir
SPECIALS_DIR = config.specials_dir
init_app = config.init_app

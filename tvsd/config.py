"""This module provides the TVSD config functionality."""
# tvsd/config.py

import configparser
import os
from pathlib import Path

import typer

from tvsd import DIR_ERROR, FILE_ERROR, SUCCESS, state

config_parser = configparser.ConfigParser()

CONFIG_DIR_PATH = Path(typer.get_app_dir(__name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"


class Config:
    """Config class"""

    def __init__(self):
        typer.echo("Config file location: " + str(CONFIG_FILE_PATH))
        config_parser.read(CONFIG_FILE_PATH)

    @classmethod
    def init_app(cls) -> int:
        """Initialize the application."""
        config_code = cls._init_config_file()
        if config_code != SUCCESS:
            return config_code
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
        """Validate the config file."""
        if not os.path.exists(CONFIG_FILE_PATH):
            self._init_config_file()
        if not config_parser.has_section("General"):
            config_parser["General"] = {
                "base_path": "/Volumes/Viewable",
                "temp_base_path": f"{os.path.expanduser('~')}/Movies/temp-parts",
                "series_dir": "TV Series",
                "specials_dir": "Specials",
            }

    @property
    def temp_base_path(self) -> str:
        """Get the base path for temporary files.

        Returns:
            str: Relative path to base path for temporary files
        """
        try:
            self.validate_config_file()
            return (
                config_parser["General"]["temp_base_path"]
                or config_parser["General"]["downloads_path"]
            )
        except KeyError:
            return "~/Movies/temp-parts"

    @property
    def base_path(self) -> str:
        """Get the base path for media files.

        Returns:
            str: Relative path to base path for media files
        """
        try:
            self.validate_config_file()
            return config_parser["General"]["base_path"]
        except KeyError:
            return "/Volumes/Viewable"

    @property
    def series_dir(self) -> str:
        """Get the directory containing TV series.


        Returns:
            str: Relative path to directory containing TV series
        """
        try:
            self.validate_config_file()
            return config_parser["General"]["series_dir"]
        except KeyError:
            return "TV Series"

    @property
    def specials_dir(self) -> str:
        """Get the directory containing TV specials.

        Returns:
            str: Relative path to directory containing TV specials
        """
        try:
            self.validate_config_file()
            return config_parser["General"]["specials_dir"]
        except KeyError:
            return "Specials"


config = Config()


def apply_config() -> None:
    """Apply the config to the state."""

    state["base_path"] = config.base_path
    state["temp_base_path"] = config.temp_base_path
    state["series_dir"] = config.series_dir
    state["specials_dir"] = config.specials_dir


validate_config_file = config.validate_config_file
init_app = config.init_app

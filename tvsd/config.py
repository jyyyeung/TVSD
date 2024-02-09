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
    """A class for managing configuration settings for the TVSD application."""

    def __init__(self):
        """
        Initializes a new instance of the Config class.

        Reads the configuration file located at the path specified by the CONFIG_FILE_PATH constant.
        """
        typer.echo("Config file location: " + str(CONFIG_FILE_PATH))
        config_parser.read(CONFIG_FILE_PATH)

    @classmethod
    def init_app(cls) -> int:
        """
        Initialize the application.

        Returns:
            int: A status code indicating whether the initialization was successful.
        """
        config_code = cls._init_config_file()
        if config_code != SUCCESS:
            return config_code
        return SUCCESS

    @classmethod
    def _init_config_file(cls) -> int:
        """
        Initializes the configuration file by creating the directory and file if they do not exist.

        Returns:
            int: A status code indicating the success or failure of the operation.
        """
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
        """Validate the config file.

        If the config file does not exist, it will be initialized with default values.
        If the "General" section is missing from the config file, it will be added with default values.
        """
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

        This method returns the relative path to the base path for temporary files. If the configuration file
        contains a value for `temp_base_path`, that value will be returned. Otherwise, the value for
        `downloads_path` will be returned. If neither value is present in the configuration file, the default
        value of `~/Movies/temp-parts` will be returned.

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

        This method returns the relative path to the base path for media files. If the path is not found in the configuration
        file, the default value "/Volumes/Viewable" is returned.

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

        This method returns the relative path to the directory containing TV series. If the configuration file
        is missing the required information, the default value "TV Series" is returned.

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

        This method returns the relative path to the directory containing TV specials.
        If the path is not specified in the configuration file, the default value "Specials" is returned.

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
    """
    Apply the configuration settings to the state.

    This function sets the values of various state variables based on the values
    specified in the configuration file. Specifically, it sets the following
    variables:

    - `state["base_path"]`: The base path for the TV show library.
    - `state["temp_base_path"]`: The temporary base path for the TV show library.
    - `state["series_dir"]`: The directory where TV show series are stored.
    - `state["specials_dir"]`: The directory where TV show specials are stored.
    """
    state["base_path"] = config.base_path
    state["temp_base_path"] = config.temp_base_path
    state["series_dir"] = config.series_dir
    state["specials_dir"] = config.specials_dir


validate_config_file = config.validate_config_file
init_app = config.init_app

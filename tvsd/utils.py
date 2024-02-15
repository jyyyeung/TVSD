"""
TVSD Utilities, contains useful functions
"""

import logging
import mimetypes
import os
import re
from typing import List

import cloudscraper
import typer

from tvsd._variables import state_base_path, state_series_dir, state_specials_dir

# from tvsd.config import BASE_PATH, SPECIALS_DIR


SCRAPER = cloudscraper.create_scraper(
    delay=10,
    # browser={
    #     "custom": "ScraperBot/1.0",
    # },
    browser={
        "browser": "chrome",
        "platform": "windows",
        "desktop": True,
        "mobile": False,
    },
)


def mkdir_if_no(check_dir: str, recursive: bool = True) -> None:
    """Creates a directory if it does not exist

    Args:
        check_dir (str): Directory to check
    """
    if not os.path.isdir(check_dir):
        if recursive:
            os.makedirs(check_dir, exist_ok=True)
        else:
            try:
                os.mkdir(check_dir)
            except FileNotFoundError:
                logging.error(
                    "Parent directory does not exist, cannot create directory %s",
                    {check_dir},
                )


def mkdir_from_base(check_dir: str) -> None:
    """
    Creates a directory from the base path.

    Args:
        check_dir (str): Directory to check.
    """
    mkdir_if_no(os.path.join(state_base_path(), check_dir))


def relative_to_absolute_path(path: str) -> str:
    """Converts a relative path to an absolute path

    Args:
        path (str): Relative path

    Returns:
        str: Absolute path
    """
    return os.path.join(state_base_path(), path)


def file_exists(file_path: str) -> bool:
    """Checks if a file exists

    Args:
        file_path (str): Path to file

    Returns:
        bool: True if file exists
    """
    return os.path.isfile(file_path)


def file_exists_in_base(file_path: str) -> bool:
    """Checks if a file exists in the base path

    Args:
        file_path (str): Path to file

    Returns:
        bool: True if file exists
    """
    return file_exists(os.path.join(state_base_path(), file_path))


def get_next_specials_index(show_dir: str) -> int:
    """
    Gets the next specials index.

    Args:
        show_dir (str): Path to show directory.

    Returns:
        int: Next specials index.
    """
    existing_episode_indexes: List[int] = []
    specials_dir: str = os.path.join(show_dir, state_specials_dir())
    if os.path.exists(specials_dir):
        for existing_special in os.listdir(specials_dir):
            match: re.Match[str] | None = re.search(r"S00E(\d{2})", existing_special)
            if match:
                existing_episode_indexes.append(int(match.group(1)))
        existing_episode_indexes.sort()
        if existing_episode_indexes:
            return existing_episode_indexes[-1]
    return 0


def check_dir_mounted(path: str) -> bool:
    """
    Check if a directory is mounted and exists.

    Args:
        path (str): The path to check.

    Returns:
        bool: True if the directory exists and is mounted, False otherwise.
    """
    if not os.path.ismount(path) and not os.path.isdir(path):
        print(path, "has not been mounted yet. Exiting...")
        return False
    if not os.path.isdir(os.path.join(path, state_series_dir())):
        print(f"{path} does not contain a {state_series_dir()} directory.")
        if (
            typer.prompt(
                "Would you like to create it? [y/n]", default="y", show_default=True
            ).capitalize()
            == "Y"
        ):
            mkdir_if_no(os.path.join(path, state_series_dir()))
        else:
            return False
    return True


def _detect_video_mimetype(video_path: str) -> str:
    """
    Detects the mimetype of a video file.

    Args:
        video_path (str): The path to the video file.

    Returns:
        str: The mimetype of the video file.
    """
    mimetypes.init()
    mimestart: str | None = mimetypes.guess_type(video_path)[0]

    if mimestart is not None:
        mimestart = mimestart.split("/")[0]
        return mimestart
    return ""


def is_video(video_path: str) -> bool:
    """
    Checks if a file is a video.

    Args:
        video_path (str): Path to video file.

    Returns:
        bool: True if the file is a video, False otherwise.
    """
    return _detect_video_mimetype(video_path) == "video"


def video_in_dir(dir_path: str, recursive: bool = True) -> bool:
    """Checks if a directory contains a video

    Args:
        dir_path (str): Path to directory
        recursive (bool, optional): Whether to search recursively. Defaults to True.

    Returns:
        bool: True if directory contains a video
    """
    for file in os.listdir(dir_path):
        if is_video(os.path.join(dir_path, file)):
            return True
        if os.path.isdir(os.path.join(dir_path, file)) and recursive:
            if video_in_dir(os.path.join(dir_path, file)):
                return True
    return False

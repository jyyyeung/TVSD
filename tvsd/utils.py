"""
TVSD Utilities, contains useful functions
"""

import logging
import mimetypes
import os
import re
from typing import Callable, List

import cloudscraper
import typer
from docstring_parser import parse

from .config import settings

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


def mkdir_from_base(subdir: str) -> None:
    """
    Creates a directory from media root.

    Args:
        subdir (str): Directory to create.
    """
    mkdir_if_no(os.path.join(settings.MEDIA_ROOT, subdir))


def relative_to_absolute_path(path: str) -> str:
    """Converts a relative path to an absolute path

    Args:
        path (str): Relative path

    Returns:
        str: Absolute path
    """
    return os.path.join(settings.MEDIA_ROOT, path)


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
    return file_exists(os.path.join(settings.MEDIA_ROOT, file_path))


def get_next_specials_index(show_dir: str) -> int:
    """
    Gets the next specials index.

    Args:
        show_dir (str): Path to show directory.

    Returns:
        int: Next specials index.
    """
    existing_episode_indexes: List[int] = []
    specials_dir: str = os.path.join(show_dir, settings.SPECIALS_DIR)
    if os.path.exists(specials_dir):
        for existing_special in os.listdir(specials_dir):
            match: re.Match[str] | None = re.search(r"S00E(\d{2})", existing_special)
            if match:
                existing_episode_indexes.append(int(match.group(1)))
        existing_episode_indexes.sort()
        if existing_episode_indexes:
            return existing_episode_indexes[-1]
    return 0


def dir_exists(path: str, create_if_not: bool = False) -> bool:
    """
    Check if a directory is mounted and exists.

    Args:
        path (str): The path to check.

    Returns:
        bool: True if the directory exists and is mounted, False otherwise.
    """
    logging.info("Checking if %s exists...", path)
    if not os.path.ismount(path) and not os.path.isdir(path):
        logging.info("%s has not been mounted or does not exist. ", path)
        if create_if_not:
            logging.info("Creating %s...", path)
            mkdir_if_no(path)

        else:
            logging.error("%s does not exist and create is False! Exiting...", path)
            return False

    return True


def check_subdir_exists(base_path: str, subdir: str) -> bool:
    if not os.path.isdir(os.path.join(base_path, subdir)):
        print(f"{base_path} does not contain a {subdir} directory.")
        if (
            typer.prompt(
                "Would you like to create it? [y/n]", default="y", show_default=True
            ).capitalize()
            == "Y"
        ):
            mkdir_if_no(os.path.join(base_path, subdir))
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


def typer_easy_cli(func):
    """
    A decorator that takes a fully-annotated function and transforms it into a
    Typer command.
    Based on: https://github.com/tiangolo/typer/issues/336#issuecomment-1251698736

    At the moment, the function needs to have only keywords at the moment, so this is ok:

    def fun(*, par1: int, par2: float):
        ...

    but this is NOT ok:

    def fun(par1: int, par2: float):
        ...
    """

    # Parse docstring
    docstring = parse(func.__doc__)

    # Collect information about the parameters of the function
    parameters = {}

    # Parse the annotations first, so we have every parameter in the
    # dictionary
    for par, par_type in func.__annotations__.items():
        parameters[par] = {"default": ...}

    # Now loop over the parameters defined in the docstring to extract the
    # help message (if present)
    for par in docstring.params:
        if par.arg_name in parameters:
            parameters[par.arg_name]["help"] = par.description

    # Finally loop over the defaults to populate that
    if not hasattr(func, "__kwdefaults__"):
        func.__kwdefaults__ = {}
    for par, default in func.__kwdefaults__.items():
        if isinstance(default, typer.models.OptionInfo):
            # if type is typer.Option, then it's already been set
            parameters[par] = default
        else:
            # if type is not typer.Option, then pass it to typer.Option
            parameters[par]["default"] = default
            parameters[par] = typer.Option(**parameters[par])

    # Transform the parameters into typer.Option instances
    typer_args = {par: kw for par, kw in parameters.items()}

    # Assign them to the function
    func.__kwdefaults__ = typer_args

    if docstring.short_description is None:
        docstring.short_description = ""

    if docstring.long_description is None:
        docstring.long_description = ""

    # Only keep the main description as docstring so the CLI won't print
    # the whole docstring, including the parameters
    func.__doc__ = "\n\n".join(
        [docstring.short_description, docstring.long_description]
    )

    return func

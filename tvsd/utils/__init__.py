import os
import re
from typing import List
import cloudscraper

# from MOV import MOV
# from OLEVOD import OLEVOD
# from Show import Source
# from XiaoBao import XiaoBao
# from YingHua import YingHua

SCRAPER = cloudscraper.create_scraper(
    delay=10,
    browser={
        "custom": "ScraperBot/1.0",
    },
)


def mkdir_if_no(check_dir: str):
    """Creates a directory if it does not exist

    Args:
        check_dir (str): Directory to check
    """
    if not os.path.isdir(check_dir):
        os.mkdir(check_dir)


def mkdir_from_base(check_dir: str):
    """Creates a directory from the base path

    Args:
        check_dir (str): Directory to check
    """
    base_path: str | None = os.getenv("DEST_PATH")
    mkdir_if_no(os.path.join(base_path, check_dir))


def relative_to_absolute_path(path: str) -> str:
    """Converts a relative path to an absolute path

    Args:
        path (str): Relative path

    Returns:
        str: Absolute path
    """
    return os.path.join(os.getenv("DEST_PATH"), path)


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
    return file_exists(os.path.join(os.getenv("DEST_PATH"), file_path))


def get_next_specials_index(show_dir: str) -> int:
    """Gets the next specials index

    Args:
        show_dir (str): Path to show directory

    Returns:
        int: Next specials index
    """
    existing_episode_indexes: List[int] = []
    specials_dir = show_dir + "/Specials"
    if os.path.exists(specials_dir):
        for existing_special in os.listdir(specials_dir):
            try:
                existing_episode_indexes += re.search(
                    r"S00E(\d{2})", existing_special
                ).groups()
            except AttributeError:
                print("No Existing Specials")
        existing_episode_indexes.sort()
        if len(existing_episode_indexes) > 0:
            return int(existing_episode_indexes[-1])
    return 0


def check_dir_mounted(path: str):
    """
    Check if a directory exists
    :param path: Path to check
    :type path: str
    """

    if not (os.path.ismount(path) and os.path.isdir(path + "/TV Series")):
        print(path, "has not been mounted yet. Exiting...")
        os.system.exit(1)

""" 
TVSD init module
"""
import importlib.metadata

from typer import Typer

_DISTRIBUTION_METADATA = importlib.metadata.metadata("tvsd")
__version__ = _DISTRIBUTION_METADATA["Version"]
__app_name__ = "tvsd"


app = Typer(name=__name__, rich_markup_mode="rich")
state = {
    "verbose": False,
    "series_dir": "TV Series",
    "specials_dir": "Specials",
    "base_path": "/Volumes/Viewable",
    "temp_base_path": "/Volumes/Viewable/temp",
}


(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
) = range(3)

ERRORS = {
    DIR_ERROR: "config directory error",
    FILE_ERROR: "config file error",
}

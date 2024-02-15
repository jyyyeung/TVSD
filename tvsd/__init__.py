"""
TVSD init module
"""

from importlib.metadata import PackageMetadata, metadata

from typer import Typer

_DISTRIBUTION_METADATA: PackageMetadata = metadata("tvsd")
__version__: str = _DISTRIBUTION_METADATA["Version"]
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

ERRORS: dict[int, str] = {
    DIR_ERROR: "config directory error",
    FILE_ERROR: "config file error",
}

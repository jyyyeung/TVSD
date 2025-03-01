"""
TVSD init module
"""

import importlib.metadata
from importlib.metadata import PackageMetadata
from typing import Dict, Optional

from typer import Typer

__app_name__ = "tvsd"

try:
    _DISTRIBUTION_METADATA: PackageMetadata = importlib.metadata.metadata("tvsd")
    __version__ = _DISTRIBUTION_METADATA["Version"]
except importlib.metadata.PackageNotFoundError:
    # If running from source or in development mode
    __version__ = "0.0.0.dev0"

app: Dict[str, Optional[str]] = {
    "name": __app_name__,
    "version": __version__,
}

app = Typer(
    name=__name__,
    rich_markup_mode="rich",
    invoke_without_command=True,
    no_args_is_help=True,
)

(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
) = range(3)

ERRORS: dict[int, str] = {
    DIR_ERROR: "config directory error",
    FILE_ERROR: "config file error",
}

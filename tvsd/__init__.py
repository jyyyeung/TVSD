__app_name__ = "tvsd"
__version__ = "1.0.0-a.1"

import os
from typer import Typer


app = Typer(name=__app_name__, rich_markup_mode="rich")
state = {"verbose": False}
current_dir = os.getcwd()


(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    JSON_ERROR,
    ID_ERROR,
) = range(7)

ERRORS = {
    DIR_ERROR: "config directory error",
    FILE_ERROR: "config file error",
    DB_READ_ERROR: "database read error",
    DB_WRITE_ERROR: "database write error",
    ID_ERROR: "to-do id error",
}

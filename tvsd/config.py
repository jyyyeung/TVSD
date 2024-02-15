"""This module provides the TVSD config functionality."""

# tvsd/config.py
import pathlib
from pathlib import Path

import typer
from dynaconf import Dynaconf, LazySettings, Validator

CONFIG_DIR_PATH = Path(typer.get_app_dir(__name__))


settings: LazySettings = Dynaconf(
    envvar_prefix="TVSD",
    settings_files=["settings.yaml"],
    environments=True,
    load_dotenv=True,
    ignore_unknown_envvars=True,
    default_env="default",
    # validate_on_update=True,
    validate_only_current_env=True,
    pretty_exceptions_short=True,
    pretty_exceptions_show_locals=False,
)


def register_validators() -> None:
    settings.validators.register(
        Validator("MEDIA_ROOT", cast=Path, must_exist=True),
        Validator("TEMP_ROOT", cast=Path, must_exist=True),
        Validator("CREATE_MEDIA_ROOT", cast=bool, must_exist=True, default=False),
        Validator("CREATE_TEMP_ROOT", cast=bool, must_exist=True, default=False),
        Validator("SERIES_DIR", cast=str, must_exist=True, default="Series"),
        Validator("SPECIALS_DIR", cast=str, must_exist=True, default="Specials"),
    )


class ConfigError(Exception):
    pass


def update_settings_path(
    path_param: str,
) -> None:
    # Taken from: https://github.com/MerginMaps/db-sync/blob/master/config.py
    config_file_path = pathlib.Path(path_param)

    if config_file_path.exists():
        print(f"Using config file: {path_param}")
        user_file_config = Dynaconf(
            # envvar_prefix=False,
            settings_files=[config_file_path],
        )
        settings.update(user_file_config)
    else:
        raise IOError(f"Config file {config_file_path} does not exist.")

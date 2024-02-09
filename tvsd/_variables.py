from tvsd import state


def state_base_path():
    """
    Returns the base path of the current state.
    """
    return state["base_path"]


def state_temp_base_path():
    """
    Returns the base path for temporary files used by the TVSD state.
    """
    return state["temp_base_path"]


def state_series_dir():
    """
    Returns the directory where the series data is stored.
    """
    return state["series_dir"]


def state_specials_dir():
    """
    Returns the directory where special files are stored in the state dictionary.
    """
    return state["specials_dir"]

from tvsd import state


def state_base_path():
    return state["base_path"]


def state_temp_base_path():
    return state["temp_base_path"]


def state_series_dir():
    return state["series_dir"]


def state_specials_dir():
    return state["specials_dir"]

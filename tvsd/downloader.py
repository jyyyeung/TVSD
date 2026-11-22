"""Download engine: m3u8 (HLS) -> mp4, backed by yt-dlp.

TVSD's own code decides *what* to download (which show, which m3u8 URL, which
filename Plex should see). Turning that m3u8 into a playable mp4 is delegated to
yt-dlp, which is maintained upstream, and gives retries, resume and progress for
free. yt-dlp needs ffmpeg to remux the HLS segments into mp4.
"""

import logging
import os
import shutil
from typing import Dict, Optional

YT_DLP_HINT = "Install it with `pip install yt-dlp` or `brew install yt-dlp`."
FFMPEG_HINT = "yt-dlp needs ffmpeg to remux HLS (m3u8/TS) streams into mp4."


class DownloadEngineError(RuntimeError):
    """Raised when the download engine (yt-dlp/ffmpeg) cannot run."""


def _find_tool(name: str, hint: str) -> str:
    """Return the path of an executable, raising DownloadEngineError if missing."""
    path = shutil.which(name)
    if path is None:
        raise DownloadEngineError(f"`{name}` was not found on PATH. {hint}")
    return path


def check_engine() -> Dict[str, str]:
    """Check that the download engine is usable.

    Returns:
        Dict[str, str]: Paths of the ``ffmpeg`` and ``yt-dlp`` executables.

    Raises:
        DownloadEngineError: If ffmpeg or yt-dlp is missing.
    """
    tools = {
        "ffmpeg": _find_tool("ffmpeg", FFMPEG_HINT),
        "yt-dlp": _find_tool("yt-dlp", YT_DLP_HINT),
    }
    return tools


def download_m3u8(
    m3u8_url: str,
    dest_dir: str,
    filename: str,
    temp_dir: Optional[str] = None,
    referer: Optional[str] = None,
) -> str:
    """Download an m3u8 stream into an mp4 file.

    Args:
        m3u8_url (str): The resolved m3u8 url of the episode.
        dest_dir (str): Directory the finished mp4 is written to.
        filename (str): Filename without extension, e.g. ``Show - S01E01 - Title``.
        temp_dir (str, optional): Directory for partial downloads. Defaults to dest_dir.
        referer (str, optional): Referer header the CDN may require.

    Returns:
        str: Path of the downloaded mp4 file.

    Raises:
        DownloadEngineError: If the engine is missing or produced no file.
    """
    check_engine()

    try:
        import yt_dlp
    except ImportError as error:  # pragma: no cover - depends on install
        raise DownloadEngineError(f"`yt_dlp` is not installed. {YT_DLP_HINT}") from error

    os.makedirs(dest_dir, exist_ok=True)
    temp_path = temp_dir or dest_dir
    os.makedirs(temp_path, exist_ok=True)

    options = {
        "format": "bv*+ba/b",
        "outtmpl": {"default": f"{filename}.%(ext)s"},
        "paths": {"home": dest_dir, "temp": temp_path},
        "merge_output_format": "mp4",
        "remux_video": "mp4",
        "noplaylist": True,
        "continuedl": True,
        "retries": 5,
        "fragment_retries": 10,
        "concurrent_fragment_downloads": 4,
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "logger": logging.getLogger("yt-dlp"),
    }
    if referer:
        options["http_headers"] = {"Referer": referer}

    logging.debug("yt-dlp downloading %s -> %s", m3u8_url, os.path.join(dest_dir, filename))

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([m3u8_url])

    destination = os.path.join(dest_dir, f"{filename}.mp4")
    if not os.path.isfile(destination):
        leftovers = [
            name for name in os.listdir(dest_dir) if name.startswith(f"{filename}.")
        ]
        raise DownloadEngineError(
            f"yt-dlp finished but {destination} does not exist "
            f"(files present: {leftovers or 'none'})."
        )

    return destination

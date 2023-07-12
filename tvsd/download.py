import os
import shutil
from typing import Literal

import m3u8_To_MP4
import typer

from multipledispatch import dispatch
from tvsd.config import BASE_PATH, TEMP_BASE_PATH

from tvsd.show import Show
from tvsd.season import Season
from tvsd.episode import Episode
from tvsd.utils import LOGGER, mkdir_if_no


class Download:
    """Download class"""

    def __init__(
        self,
        target: Show | Season | Episode,
        base_path: str = BASE_PATH,
        temp_path: str = TEMP_BASE_PATH,
    ):
        self._target: Show | Season | Episode = target
        self._base_path = base_path
        self._temp_base_path = temp_path
        self._target_path: str
        self._specials_index: int = 1
        self._regular_ep_index: int = 1

    def guided_download(self):
        """Guided download of show"""

        # TODO: Check monitor file in directory, check files not downloaded
        #  IDEA: it is known that hash is unique for a
        #  video, if so, hash can be matched to ensure there are no additional ads embedded in videos
        download_all: bool = (
            typer.prompt(
                text="Would you like to download all episodes?",
                type=str,
                default="Y",
            ).capitalize()
            == "Y"
        )

        if download_all:
            self.download_all(self._target)
        else:
            self.choose_download(self._target)

    def choose_download(self, season: "Season"):
        """Choose download of show"""
        for episode in season.episodes:
            if (
                typer.prompt(
                    text=f"Would you like to download this {episode.name}?",
                    type=str,
                    default="n",
                ).capitalize()
                == "Y"
            ):
                self.download_episode(episode)
            else:
                self.set_ep_index(episode)

    @dispatch(Show)
    def download_all(self, show: Show):
        """Download all episodes in a show"""
        LOGGER.debug("Downloading all episodes in show")
        for season in show.seasons:
            self.download_all(season)

    @dispatch(Season)
    def download_all(self, season: Literal["Season"]):
        """Download all episodes in a season"""
        LOGGER.info("Downloading all episodes in season")

        # reset episode index
        self._specials_index = 1
        self._regular_ep_index = 1

        for episode in season.episodes:
            self.download_episode(episode)

    def set_special_ep_index(self, episode: "Episode"):
        """Set index for special episode

        Args:
            episode (Episode): Episode to set index for
        """
        episode.episode_number = self._specials_index
        self._specials_index += 1

    def set_regular_ep_index(self, episode: "Episode"):
        """Set index for regular episode

        Args:
            episode (Episode): Episode to set index for
        """
        episode.episode_number = self._regular_ep_index
        self._regular_ep_index += 1

    def set_ep_index(self, episode: "Episode"):
        """Set index for episode

        Args:
            episode (Episode): Episode to set index for
            index (int): Index to set
        """
        if episode.is_specials:
            self.set_special_ep_index(episode)
        else:
            self.set_regular_ep_index(episode)

    @dispatch(Episode)
    def download_all(self, episode: "Episode"):
        """Download episode"""

        self.download_episode(episode)

    def download_episode(self, episode: "Episode"):
        """Download an episode

        Args:
            episode (Episode): Episode to download
        """

        self.set_ep_index(episode)

        absolute_dest_dir = os.path.join(
            self._base_path, episode.relative_destination_dir
        )
        LOGGER.info(absolute_dest_dir)
        mkdir_if_no(absolute_dest_dir)

        if episode.file_exists_locally:
            return

        print(f"Downloading to file {episode.filename}")

        episode_m3u8: str = episode.fetch_episode_m3u8_url or ""

        # TODO: Background download

        # m3u8_To_MP4.multithread_uri_download(m3u8_uri=episode_m3u8,
        # mp4_file_name=episode_filename, mp4_file_dir=show_dir)
        if "m3u8" not in episode_m3u8:
            print("m3u8 Load Error, Stream probably does not exist: " + episode_m3u8)
            return

        temp_dir = os.path.join(self._temp_base_path, episode.filename)
        if not os.path.isdir(temp_dir):
            mkdir_if_no(temp_dir)
            m3u8_To_MP4.multithread_uri_download(
                m3u8_uri=episode_m3u8,
                mp4_file_name=episode.filename,
                mp4_file_dir=absolute_dest_dir,
                tmpdir=temp_dir,
            )
            print("Completed downloading, removing temp dir...")
            shutil.rmtree(temp_dir, ignore_errors=True)
        else:
            print("Temp Dir for this episode exists, should be already downloading")

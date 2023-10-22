"""TVSD Download Class"""
import logging
import os
import shutil

import m3u8_To_MP4
import typer

from tvsd._variables import state_base_path, state_temp_base_path
from tvsd.types.episode import Episode
from tvsd.types.season import Season
from tvsd.types.show import Show
from tvsd.utils import mkdir_if_no


class Download:
    """Download class"""

    def __init__(
        self,
        target: Show | Season | Episode,
        base_path: str = state_base_path(),
        temp_path: str = state_temp_base_path(),
        specials_only: bool = False,
    ):
        self._target: Show | Season | Episode = target
        self._base_path = base_path
        self._temp_base_path = temp_path

        self._specials_index: int = 1
        self._regular_ep_index: int = 1

        self._specials_only = specials_only

    def guided_download(self):
        """
        guided_download Guided download of show
        """

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
            assert isinstance(self._target, Season)
            self.choose_download(self._target)

    def choose_download(self, season: "Season"):
        """
        choose_download Choose Episodes in Season to download

        Args:
            season (Season): Season to choose episodes from
        """
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

    def download_all(self, target: "Season| Show| Episode"):
        """
        download_all Download all episodes under the specified Season/Show/Episode

        Args:
            target (Season| Show| Episode): Season/Show/Episode to download

        Raises:
            TypeError: Target must be Show, Season or Episode
        """
        if isinstance(target, Show):
            # Target is Show, download all seasons
            logging.debug("Downloading all episodes in show")
            for season in target.seasons:
                self.download_all(season)

        elif isinstance(target, Season):
            # Target is Season, download entire season
            logging.info("Downloading all episodes in season")

            # reset episode index
            self._specials_index = 1
            self._regular_ep_index = 1

            for episode in target.episodes:
                self.download_episode(episode)

        elif isinstance(target, Episode):
            # download episode

            self.download_episode(target)

        else:
            raise TypeError("Target must be Show, Season or Episode")

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
            index (int): Index to set as episode number
        """
        if episode.is_specials:
            self.set_special_ep_index(episode)
        else:
            self.set_regular_ep_index(episode)

    def download_episode(self, episode: "Episode"):
        """Download an episode

        Args:
            episode (Episode): Episode to download

        Raises:
            ValueError: m3u8 not found in episode url, Stream probably does not exist
        """
        if self._specials_only and not episode.is_specials:
            logging.info("Skipping regular episode (--specials-only)")
            return

        absolute_dest_dir = os.path.join(
            self._base_path, episode.relative_destination_dir
        )
        logging.info(absolute_dest_dir)
        mkdir_if_no(absolute_dest_dir)

        self.set_ep_index(episode)

        existing_file = episode.file_exists_locally

        if existing_file != "":
            print(f"{episode.name} already exists in directory, skipping... ")
            number = int(existing_file.split(" - ")[1].split("E")[1])
            if episode.is_specials:
                self._specials_index = number + 1
            else:
                self._regular_ep_index = number + 1

            return

        print(f"Downloading to file {episode.filename}")

        episode_m3u8: str = episode.fetch_episode_m3u8_url or ""

        # TODO: Background download

        if "m3u8" not in episode_m3u8:
            logging.debug("m3u8 Load Error: %s", episode_m3u8)
            raise ValueError(
                "m3u8 not found in episode url, Stream probably does not exist"
            )

        temp_dir = os.path.join(self._temp_base_path, episode.filename)
        if not os.path.isdir(temp_dir):
            mkdir_if_no(temp_dir)
            print(f"Downloading {episode.filename} to {absolute_dest_dir}...")
            try:
                m3u8_To_MP4.multithread_uri_download(
                    m3u8_uri=episode_m3u8,
                    mp4_file_name=episode.filename,
                    mp4_file_dir=absolute_dest_dir,
                    tmpdir=temp_dir,
                )
                print("Completed downloading, removing temp dir...")
            except Exception as error:
                print("Error downloading episode: " + str(error))
                print("Removing temp dir...")
            shutil.rmtree(temp_dir, ignore_errors=True)
        else:
            print("Temp Dir for this episode exists, should be already downloading")

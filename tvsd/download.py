"""TVSD Download Class"""

import logging
import os
import shutil

import m3u8_To_MP4
import typer

from tvsd.config import settings
from tvsd.types.episode import Episode
from tvsd.types.season import Season
from tvsd.types.show import Show
from tvsd.utils import mkdir_if_no


class Download:
    """
    A class for downloading TV show episodes.

    Attributes:
        _target (Show|Season|Episode): The target show, season or episode to download.
        _base_path (str): The base path for the downloaded files.
        _temp_base_path (str): The temporary base path for the downloaded files.
        _specials_index (int): The index for special episodes.
        _regular_ep_index (int): The index for regular episodes.
        _specials_only (bool): Whether to download only special episodes.
    """

    def __init__(
        self,
        target: Show | Season | Episode,
        specials_only: bool = False,
    ) -> None:
        """
        Initializes a new instance of the Download class.

        Args:
            target (Show|Season|Episode): The target show, season or episode to download.
            base_path (str, optional): The base path for the downloaded files. Defaults to settings.MEDIA_ROOT.
            temp_path (str, optional): The temporary base path for the downloaded files. Defaults to settings.TEMP_ROOT.
            specials_only (bool, optional): Whether to download only special episodes. Defaults to False.
        """
        self._target: Show | Season | Episode = target

        self._specials_index: int = 1
        self._regular_ep_index: int = 1

        self._specials_only: bool = specials_only

    def guided_download(self) -> None:
        """
        Guided download of show.

        This method prompts the user to choose whether to download all episodes of a show or a specific season.
        If the user chooses to download all episodes, the `download_all` method is called with the target show as the argument.
        If the user chooses to download a specific season, the `choose_download` method is called with the target season as the argument.
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

    def choose_download(self, season: "Season") -> None:
        """
        Choose which episodes in a season to download.

        Args:
            season (Season): The season to choose episodes from.
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

    def download_all(self, target: "Season| Show| Episode") -> None:
        """
        Download all episodes under the specified Season/Show/Episode.

        Args:
            target (Season| Show| Episode): The Season, Show or Episode to download.

        Raises:
            TypeError: If the target is not a Show, Season or Episode.
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

    def set_special_ep_index(self, episode: "Episode") -> None:
        """
        Set the index for a special episode.

        Args:
            episode (Episode): The episode to set the index for.
        """
        episode.episode_number = self._specials_index
        self._specials_index += 1

    def set_regular_ep_index(self, episode: "Episode") -> None:
        """
        Set the index for a regular episode.

        Args:
            episode (Episode): The episode to set the index for.
        """
        episode.episode_number = self._regular_ep_index
        self._regular_ep_index += 1

    def set_ep_index(self, episode: "Episode") -> None:
        """Set index for episode

        This method sets the index for a given episode. If the episode is a special episode, it calls the
        `set_special_ep_index` method, otherwise it calls the `set_regular_ep_index` method.

        Args:
            episode (Episode): Episode to set index for
        """
        if episode.is_specials:
            self.set_special_ep_index(episode)
        else:
            self.set_regular_ep_index(episode)

    def download_episode(self, episode: "Episode") -> None:
        """Download an episode

        Args:
            episode (Episode): Episode to download

        Raises:
            ValueError: m3u8 not found in episode url, Stream probably does not exist

        Downloads an episode by fetching its m3u8 url and converting it to an mp4 file.
        If the episode already exists in the destination directory, it skips the download.
        """
        if self._specials_only and not episode.is_specials:
            logging.info("Skipping regular episode (--specials-only)")
            return

        absolute_dest_dir = os.path.join(
            settings.MEDIA_ROOT, episode.relative_destination_dir
        )
        logging.info(absolute_dest_dir)
        mkdir_if_no(absolute_dest_dir)

        self.set_ep_index(episode)

        existing_file: str = episode.file_exists_locally

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

        temp_dir: str = os.path.join(settings.TEMP_ROOT, episode.filename)
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

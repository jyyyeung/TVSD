"""
Episode class.
"""

import os
import re
from typing import TYPE_CHECKING

from tvsd._variables import state_base_path, state_temp_base_path
from tvsd.utils import file_exists_in_base, relative_to_absolute_path

if TYPE_CHECKING:
    from tvsd.types.season import Season


class Episode:
    """Episode class"""

    def __init__(
        self,
        episode_name: str,
        episode_url: str,
        # previous_episode: "Episode" = None,
        # next_episode: "Episode" = None,
        season: "Season",
    ):
        self._name = episode_name
        self._url = episode_url
        self._number: int

        # self._previous_episode = previous_episode
        # self._next_episode = next_episode
        self._season: "Season" = season

        self._not_specials = True

    def __str__(self):
        return f"{self.name} ({self.episode_number})"

    def __repr__(self):
        return f"{self.name} ({self.episode_number})"

    def identify_episode_number_from_name(self) -> int:
        """Tries to identify the episode number from the episode name.

        Returns:
            int: The identified episode number.
        """

        try:
            print(self._name)
            episode_number_identifying_regex = r"^[0-9]{8}[（(]*第(\d+)[期集][(（上中下)）]*[)）]?$|^(\d{1,3})$|^第(\d+)[期集][上中下]*$"
            episode_number_match = re.match(
                episode_number_identifying_regex, self._name
            )

            if episode_number_match is not None:
                episode_number_groups = episode_number_match.groups()

                # Filter out all None matches
                identified_number = [i for i in episode_number_groups if i is not None][
                    0
                ]

                print(f"episode_number: {identified_number}")
                # episode_index = int(re.findall(r'\d*', episode_number)[0])
                resulting_index = int(re.findall(r"^\d{1,3}$", identified_number)[0])

                # print(episode_number)
            else:
                resulting_index = 1

        except AttributeError:
            resulting_index = 1

        self._number = resulting_index

        return resulting_index

    def determine_if_specials(self) -> bool:
        """Determines if the episode is a special episode from episode title.

        Returns:
            bool: True if the episode is a special episode, False otherwise.
        """
        specials_regex = r"^[0-9]{8}[(（上中下)）]*$|^[0-9]{8}[（(]*第([0-9]+)[期集][(（上中下)）]*[)）]?$|^([0-9]{1,3})$|^第([0-9]+)[期集][上中下]*$"
        not_specials = re.match(specials_regex, self._name)
        self._not_specials = not_specials
        return not not_specials

    @property
    def is_specials(self) -> bool:
        """Returns True if the episode is a special episode, False otherwise.

        Returns:
            bool: True if the episode is a special episode, False otherwise.
        """
        return self.determine_if_specials()

    @property
    def is_regular(self) -> bool:
        """Returns True if the episode is a regular episode, False otherwise.

        Returns:
            bool: True if the episode is a regular episode, False otherwise.
        """
        return not self.determine_if_specials()

    @property
    def episode_number(self) -> int:
        """Returns the episode number.

        Returns:
            int: The episode number.
        """
        if self._number is None:
            self.identify_episode_number_from_name()
        return self._number

    @episode_number.setter
    def episode_number(self, episode_number: int):
        """Sets the episode number."""
        self._number = episode_number

    @property
    def determine_episode_number(self) -> int:
        """Determines the episode number.

        Returns:
            int: The episode number.
        """
        index = (
            # self._previous_episode.episode_number + 1
            # or
            self.identify_episode_number_from_name()
        )
        self._number = index
        return index

    @property
    def name(self) -> str:
        """Returns the episode name.

        Returns:
            str: The episode name.
        """
        # TODO: Temporary solution, check if 中 exists
        # if "（上" in episode_name or "期上" in episode_name:
        #     episode_name = "part1"
        # elif "（下" in episode_name or "期下" in episode_name:
        #     episode_name = "part2"
        return self._name

    @property
    def filename(self) -> str:
        """Returns the filename of the episode.

        Returns:
            str: The filename of the episode.
        """
        season_index: str = (
            "00" if self.is_specials else str(self._season.season_index).zfill(2)
        )
        return f"{self.season.show.show_prefix} - S{season_index}E{str(self.episode_number).zfill(2)} - {self.name}"

    @property
    def get_episode_url(self) -> str:
        """Gets the episode url from the episode object.

        Args:
            episode (Episode): The episode object.

        Returns:
            str: The episode url.
        """
        episode_url = self._url
        return episode_url

    @property
    def relative_episode_file_path(self) -> str:
        """Returns the relative path to the episode file.

        Returns:
            str: The relative path to the episode file.
        """
        return f"{self._season.relative_season_dir}/{self.filename}.mp4"

    @property
    def file_exists_locally(self) -> str:
        """Returns True if the episode exists locally, False otherwise.

        Returns:
            filename(str): Name of existing file if the episode exists locally, Empty String otherwise.
        """
        # Check if file exists already
        if file_exists_in_base(self.relative_episode_file_path):
            print(f"{self.filename} already exists in directory, skipping... ")
            return self.filename

        episode_title = self.filename.split(" - ")[-1]
        for file in os.listdir(
            os.path.join(state_base_path(), self._season.relative_season_dir)
        ):
            if episode_title in file:
                print(f"{self.filename} probably exist as {file}, skipping...")
                return file

        # file_exists(os.path.join(state_base_path(), self.relative_episode_file_path))

        # specials exists already
        for existing_episode in os.listdir(
            relative_to_absolute_path(self.relative_destination_dir)
        ):
            # print(episode_name, existing_episode)
            if existing_episode.endswith(".mp4") and episode_title in existing_episode:
                print(
                    f"{self.filename} probably exist as {existing_episode}, skipping..."
                )
                return existing_episode
        return ""

    @property
    def season(self) -> "Season":
        """Returns the season object.

        Returns:
            Season: The season object.
        """
        return self._season

    @property
    def fetch_episode_m3u8_url(self) -> str:
        """Fetches the m3u8 url of the episode.

        Returns:
            str: The m3u8 url of the episode.
        """
        return self.season.source.fetch_episode_m3u8(relative_episode_url=self._url)

    @property
    def relative_destination_dir(self) -> str:
        """Returns the relative destination directory of the episode.

        Returns:
            str: The relative destination directory of the episode.
        """
        if self.is_specials:
            return self.season.relative_specials_dir
        return self.season.relative_season_dir

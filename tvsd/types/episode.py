"""
Episode class.
"""

import logging
import os
from re import Match, findall, match
from typing import TYPE_CHECKING

from tvsd._variables import state_base_path
from tvsd.utils import file_exists_in_base, relative_to_absolute_path

if TYPE_CHECKING:
    from tvsd.types.season import Season


class Episode:
    """A class representing an episode of a TV show.

    Attributes:
        _name (str): The name of the episode.
        _url (str): The URL of the episode.
        _number (int): The episode number.
        _season (Season): The season that the episode belongs to.
        _not_specials (bool): True if the episode is not a special episode, False otherwise.
    """

    def __init__(
        self,
        episode_name: str,
        episode_url: str,
        season: "Season",
    ) -> None:
        """Initialize a new Episode object.

        Args:
            episode_name (str): The name of the episode.
            episode_url (str): The URL of the episode.
            season (Season): The season that this episode belongs to.
        """
        self._name: str = episode_name
        self._url: str = episode_url
        self._number: int

        self._season: "Season" = season

        self._not_specials = True

    def __str__(self) -> str:
        """
        Returns a string representation of the Episode object.

        The string representation includes the name and episode number of the episode.

        Returns:
            str: A string representation of the Episode object.
        """
        return f"{self.name} ({self.episode_number})"

    def __repr__(self) -> str:
        """
        Returns a string representation of the Episode object.
        The string contains the name and episode number of the episode.
        """
        return f"{self.name} ({self.episode_number})"

    def identify_episode_number_from_name(self) -> int:
        """
        Tries to identify the episode number from the episode name.

        This function uses a regular expression to identify the episode number from the episode name.
        If the episode number is found, it is returned as an integer. If it is not found, the function
        returns 1.

        Returns:
            int: The identified episode number.
        """
        try:
            print(self._name)
            episode_number_identifying_regex = r"^[0-9]{8}[（(]*第(\d+)[期集][(（上中下)）]*[)）]?$|^(\d{1,3})$|^第(\d+)[期集][上中下]*$"
            episode_number_match: Match[str] | None = match(
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
                resulting_index = int(findall(r"^\d{1,3}$", identified_number)[0])

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
        not_specials: bool = bool(match(specials_regex, self._name))
        self._not_specials: bool = not_specials
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

        If the episode number is not already set, it will be identified from the episode name.

        Returns:
            int: The episode number.
        """
        if self._number is None:
            self.identify_episode_number_from_name()
        return self._number

    @episode_number.setter
    def episode_number(self, episode_number: int) -> None:
        """
        Sets the episode number.

        Args:
            episode_number (int): The episode number to set.
        """
        self._number = episode_number

    @property
    def determine_episode_number(self) -> int:
        """Determines the episode number.

        This method determines the episode number by either incrementing the previous episode number by 1 or by identifying the episode number from the episode name. The episode number is then stored in the instance variable _number.

        Returns:
            int: The episode number.
        """
        index: int = (
            # self._previous_episode.episode_number + 1
            # or
            self.identify_episode_number_from_name()
        )
        self._number = index
        return index

    @property
    def name(self) -> str:
        """Returns the episode name.

        This method returns the name of the episode.

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

        The filename is formatted as follows:
        {show_prefix} - S{season_index}E{episode_number} - {episode_name}

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

        This method returns the url of the episode object.

        Returns:
            str: The episode url.
        """
        episode_url: str = self._url
        return episode_url

    @property
    def relative_episode_file_path(self) -> str:
        """
        Returns the relative path to the episode file.

        The returned path is relative to the root directory of the TVSD project.

        Returns:
            str: The relative path to the episode file.
        """
        return f"{self._season.relative_season_dir}/{self.filename}.mp4"

    @property
    def file_exists_locally(self) -> str:
        """Returns the name of the existing file if the episode exists locally, or an empty string otherwise.

        Returns:
            filename(str): Name of existing file if the episode exists locally, Empty String otherwise.
        """
        # Check if file exists already
        if file_exists_in_base(self.relative_episode_file_path):
            print(f"{self.filename} already exists in directory, skipping... ")
            return self.filename

        episode_title: str = self.filename.split(" - ")[-1]
        try:
            for file in os.listdir(
                os.path.join(state_base_path(), self._season.relative_season_dir)
            ):
                if episode_title in file:
                    print(f"{self.filename} probably exist as {file}, skipping...")
                    return file
        except FileNotFoundError:
            logging.debug(
                "%s does not exist, skipping file check in this directory...",
                self._season.relative_season_dir,
            )

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
        """
        Fetches the m3u8 url of the episode.

        This method fetches the m3u8 url of the episode by calling the fetch_episode_m3u8 method of the season's source object,
        passing in the relative episode url as a parameter. If the m3u8 url is not found, an empty string is returned.

        Returns:
            str: The m3u8 url of the episode.
        """
        m3u8_url: str | None = self.season.source.fetch_episode_m3u8(
            relative_episode_url=self._url
        )
        if m3u8_url is None:
            return ""
        return m3u8_url

    @property
    def relative_destination_dir(self) -> str:
        """Returns the relative destination directory of the episode.

        If the episode is a special episode, the relative destination directory
        will be the relative specials directory of the season. Otherwise, it will
        be the relative season directory of the season.

        Returns:
            str: The relative destination directory of the episode.
        """
        if self.is_specials:
            return self.season.relative_specials_dir
        return self.season.relative_season_dir

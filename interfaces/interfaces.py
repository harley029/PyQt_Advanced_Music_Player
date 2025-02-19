from abc import ABC, abstractmethod
from typing import List, Tuple, Any
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtMultimedia import QMediaPlayer


class ICommand(ABC):
    """
    Command interface. All commands must implement the execute() method.
    This interface follows the Command pattern to encapsulate actions as objects.
    """

    @abstractmethod
    def execute(self):
        """
        Executes the command's action.
        This method should contain the core logic of the command.
        """


class IPlaylistManager(ABC):
    """
    Playlist manager interface.

    Defines the contract for loading, creating, deleting playlists and managing the UI.
    This interface provides a complete abstraction for playlist operations and their
    UI representation.
    """

    @abstractmethod
    def load_playlists_into_widget(self) -> None:
        """
        Loads the list of playlists into the corresponding UI widget.
        Updates the UI to reflect the current state of available playlists.
        """

    @abstractmethod
    def load_playlist_into_widget(self, parent) -> None:
        """
        Loads the selected playlist into the songs widget.

        Args:
            parent: Parent widget containing playlist and song lists.
        """

    @abstractmethod
    def create_playlist(self, parent) -> str:
        """
        Creates a new playlist through an input dialog and updates the UI.

        Args:
            parent: Parent widget for the dialog.

        Returns:
            str: Name of the created playlist or None if operation was cancelled.
        """

    @abstractmethod
    def remove_playlist(self, parent) -> None:
        """
        Removes the selected playlist and updates the UI.

        Args:
            parent: Parent widget containing the playlist list.
        """

    @abstractmethod
    def remove_all_playlists(self, parent) -> None:
        """
        Removes all playlists and updates the UI.

        Args:
            parent: Parent widget containing the playlist list.
        """

    @abstractmethod
    def check_list_not_empty(
        self, list_widget: QListWidget, message: str = "No songs in the list!"
    ) -> bool:
        """
        Checks if the provided widget is not empty.

        Args:
            list_widget: Widget containing the list of items.
            message: Error message to display if the list is empty.

        Returns:
            bool: True if the list is not empty, False otherwise.
        """

    @abstractmethod
    def add_song_to_playlist(self, parent) -> None:
        """
        Adds the selected song to the selected playlist.

        Args:
            parent: Parent widget containing song and playlist lists.
        """

    @abstractmethod
    def add_all_to_playlist(self, parent) -> None:
        """
        Adds all songs from the list to the selected playlist.

        Args:
            parent: Parent widget containing song and playlist lists.
        """


class IPlaylistDatabaseManager(ABC):
    """
    Interface for playlist database operations.

    Provides methods for creating, deleting, and managing playlists in the database.
    This interface abstracts the underlying database implementation from the playlist
    management logic.
    """

    @abstractmethod
    def create_playlist(self, name: str):
        """
        Creates a new playlist in the database.

        Args:
            name: Name of the playlist to create.
        """

    @abstractmethod
    def delete_playlist(self, name: str):
        """
        Deletes a playlist from the database.

        Args:
            name: Name of the playlist to delete.
        """

    @abstractmethod
    def add_song_to_playlist(self, playlist: str, song: str):
        """
        Adds a song to a playlist.

        Args:
            playlist: Name of the target playlist.
            song: Path or identifier of the song to add.
        """

    @abstractmethod
    def get_playlists(self) -> List[str]:
        """
        Retrieves all playlists from the database.

        Returns:
            List[str]: List of playlist names.
        """


class IPlaylistUIManager(ABC):
    """
    Interface for managing playlist UI operations.

    Provides methods for loading and displaying playlists in the user interface.
    This interface separates UI concerns from the underlying playlist data management.
    """

    @abstractmethod
    def load_playlists(self):
        """
        Loads playlists into the UI.
        Updates the UI components to display all available playlists.
        """

    @abstractmethod
    def load_playlist(self, playlist: str, list_widget: QListWidget):
        """
        Loads a specific playlist into the UI.

        Args:
            playlist: Name of the playlist to load.
            list_widget: Widget where the playlist should be displayed.
        """

    @abstractmethod
    def check_list_not_empty(self, list_widget: QListWidget, message: str) -> bool:
        """
        Verifies that the provided widget is not empty.

        Args:
            list_widget: Widget to check.
            message: Error message to display if the list is empty.

        Returns:
            bool: True if the list contains items, False otherwise.
        """

    @abstractmethod
    def select_playlist(self, parent_widget: QListWidget):
        """
        Returns the currently selected playlist.

        Args:
            parent_widget: Widget containing the playlist list.

        Returns:
            The selected playlist or appropriate return value based on implementation.
        """


class INavigationStrategy(ABC):
    """
    Interface for navigation strategy to select next or previous songs.

    Implements the Strategy pattern for different song navigation behaviors
    (e.g., sequential, random, repeat).
    """

    @abstractmethod
    def get_next_index(self, current_index: int, count: int) -> int:
        """
        Calculates the index of the next song.

        Args:
            current_index: Current song index.
            count: Total number of songs.

        Returns:
            int: Index of the next song.
        """

    @abstractmethod
    def get_previous_index(self, current_index: int, count: int) -> int:
        """
        Calculates the index of the previous song.

        Args:
            current_index: Current song index.
            count: Total number of songs.

        Returns:
            int: Index of the previous song.
        """


class IDatabaseManager(ABC):
    """
    Interface for database operations.

    Defines methods for database connection, SQL query execution, and data operations.
    This interface allows for different database implementations (SQLite, PostgreSQL, MySQL)
    without changing the application's business logic.
    """

    @abstractmethod
    def _connect(self) -> Any:
        """
        Creates and returns a database connection.

        Returns:
            Any: Database connection object (e.g., sqlite3.Connection).
        """

    @abstractmethod
    def execute_query(
        self, query: str, params: Tuple = (), fetch: bool = False
    ) -> List[Tuple]:
        """
        Executes an SQL query on the database.

        Args:
            query: SQL query string.
            params: Tuple of parameters for parameterized query (default empty tuple).
            fetch: If True, returns query results, otherwise returns empty list.

        Returns:
            List[Tuple]: List of query results if fetch=True, empty list otherwise.
        """

    @abstractmethod
    def add_song(self, table: str, song: str) -> None:
        """
        Adds a song to the specified database table.

        Args:
            table: Name of the target table.
            song: Path or identifier of the song.
        """

    @abstractmethod
    def delete_song(self, table: str, song: str) -> None:
        """
        Removes a song from the specified database table.

        Args:
            table: Name of the target table.
            song: Path or identifier of the song to remove.
        """

    @abstractmethod
    def delete_all_songs(self, table: str) -> None:
        """
        Removes all songs from the specified database table.

        Args:
            table: Name of the table to clear.
        """

    @abstractmethod
    def create_table(self, table_name: str, columns: str = "song TEXT UNIQUE") -> None:
        """
        Creates a table in the database if it doesn't exist.

        Args:
            table_name: Name of the table to create.
            columns: String describing the columns (defaults to single unique song column).
        """

    @abstractmethod
    def delete_table(self, table: str) -> None:
        """
        Removes a table from the database if it exists.

        Args:
            table: Name of the table to delete.
        """

    @abstractmethod
    def get_tables(self) -> List[str]:
        """
        Retrieves all tables from the database.

        Returns:
            List[str]: List of table names.
        """

    @abstractmethod
    def fetch_all_songs(self, table: str) -> List[str]:
        """
        Retrieves all songs from the specified database table.

        Args:
            table: Name of the table to query.

        Returns:
            List[str]: List of songs (e.g., file paths).
        """


class IMusicPlayerController(ABC):
    """
    Interface for music player control operations.

    Provides methods for controlling music playback, volume, and playback modes.
    This interface abstracts the underlying media player implementation from the
    control logic.
    """

    @abstractmethod
    def set_volume(self, volume: int):
        """
        Sets the player volume.

        Args:
            volume: Volume level to set.
        """

    @abstractmethod
    def current_volume(self) -> int:
        """
        Gets the current volume level.

        Returns:
            int: Current volume level.
        """

    @abstractmethod
    def play_song(self, song_path: str):
        """
        Starts playing a song.

        Args:
            song_path: Path to the song file to play.
        """

    @abstractmethod
    def stop_song(self):
        """
        Stops the currently playing song.
        """

    @abstractmethod
    def pause_song(self):
        """
        Pauses the currently playing song.
        """

    @abstractmethod
    def resume_song(self):
        """
        Resumes playing the paused song.
        """

    @abstractmethod
    def is_playing(self) -> bool:
        """
        Checks if a song is currently playing.

        Returns:
            bool: True if a song is playing, False otherwise.
        """

    @abstractmethod
    def is_paused(self) -> bool:
        """
        Checks if playback is currently paused.

        Returns:
            bool: True if playback is paused, False otherwise.
        """

    @abstractmethod
    def set_looped(self, looped: bool):
        """
        Sets the loop playback mode.

        Args:
            looped: True to enable loop mode, False to disable.
        """

    @abstractmethod
    def set_shuffled(self, shuffled: bool):
        """
        Sets the shuffle playback mode.

        Args:
            shuffled: True to enable shuffle mode, False to disable.
        """

    @abstractmethod
    def media_player(self) -> QMediaPlayer:
        """
        Gets the underlying media player instance.

        Returns:
            QMediaPlayer: The Qt media player instance being used.
        """

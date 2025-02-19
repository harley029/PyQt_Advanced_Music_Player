from typing import List

from interfaces.interfaces import IPlaylistDatabaseManager
from interfaces.interfaces import IDatabaseManager


class PlaylistDatabaseManager(IPlaylistDatabaseManager):
    """
    Manages playlists in a database through implementation of the IPlaylistDatabaseManager interface.

    This class provides methods for creating, deleting, and managing playlists,
    as well as adding songs to playlists and retrieving songs from playlists.

    Attributes:
        db_manager (IDatabaseManager): The database manager instance used for database operations.
    """

    def __init__(self, db_manager: IDatabaseManager):
        """
        Initialize a new PlaylistDatabaseManager instance.

        Args:
            db_manager (IDatabaseManager): The database manager instance to use for database operations.
        """
        self.db_manager = db_manager

    def create_playlist(self, name: str):
        """
        Create a new playlist if it doesn't already exist.

        Args:
            name (str): The name of the playlist to create.
        """
        existing_playlists = self.get_playlists()
        if name not in existing_playlists:
            self.db_manager.create_table(name)

    def delete_playlist(self, name: str):
        """
        Delete an existing playlist.

        Args:
            name (str): The name of the playlist to delete.
        """
        self.db_manager.delete_table(name)

    def get_playlists(self) -> List[str]:
        """
        Get a list of all playlists, excluding the 'favourites' playlist.

        Returns:
            List[str]: A list of playlist names, excluding 'favourites'.
        """
        playlists = self.db_manager.get_tables()
        if "favourites" in playlists:
            playlists.remove("favourites")
        return playlists

    def add_song_to_playlist(self, playlist: str, song: str):
        """
        Add a song to the specified playlist.

        Args:
            playlist (str): The name of the playlist to add the song to.
            song (str): The song to add to the playlist.
        """
        self.db_manager.add_song(playlist, song)

    def fetch_all_songs(self, playlist: str):
        """
        Fetches all songs from the specified playlist.

        Args:
            playlist (str): The name of the playlist from which to fetch all songs.

        Returns:
            List[str]: A list of all songs in the specified playlist.
        """
        return self.db_manager.fetch_all_songs(playlist)

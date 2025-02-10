from typing import List

from interfaces.interfaces import IPlaylistDatabaseManager
from interfaces.interfaces import IDatabaseManager


class PlaylistDatabaseManager(IPlaylistDatabaseManager):

    def __init__(self, db_manager: IDatabaseManager):
        self.db_manager = db_manager

    def create_playlist(self, name: str):
        existing_playlists = self.get_playlists()
        if name not in existing_playlists:
            self.db_manager.create_table(name)

    def delete_playlist(self, name: str):
        self.db_manager.delete_table(name)

    def get_playlists(self) -> List[str]:
        playlists = self.db_manager.get_tables()
        if "favourites" in playlists:
            playlists.remove("favourites")
        return playlists

    def add_song_to_playlist(self, playlist: str, song: str):
        self.db_manager.add_song(playlist, song)

    def remove_song_from_playlist(self, playlist: str, song: str):
        self.db_manager.delete_song(playlist, song)

    def fetch_all_songs(self, playlist: str):
        return self.db_manager.fetch_all_songs(playlist)

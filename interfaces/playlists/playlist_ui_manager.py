import os
from enum import Enum

from PyQt5.QtWidgets import QListWidget, QInputDialog, QListWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from interfaces.interfaces import IPlaylistUIManager


class IconType(Enum):
    """
    Enum defining icon paths for different playlist types.
    Provides consistent access to icon resources.
    """
    FAVOURITE = ":/img/utils/images/like.png"
    DEFAULT = ":/img/utils/images/MusicListItem.png"


class PlaylistUIManager(IPlaylistUIManager):
    """
    Implementation of IPlaylistUIManager for managing playlist display.
    This class only receives the necessary widgets (for example, a widget for the playlist list)
    and operates independently of the rest of the main window.
    """

    def __init__(self, playlist_widget: QListWidget, db_manager, icon_config=None):
        """
        Initializes the PlaylistUIManager with necessary components.

        Args:
            playlist_widget (QListWidget): Widget where playlist names will be loaded.
            db_manager: Object implementing database operations for playlists.
            icon_config (dict, optional): Configuration mapping playlist types to icons.
        """
        self.playlist_widget = playlist_widget
        self.db_manager = db_manager
        self.icon_config = icon_config or {
            "favourites": IconType.FAVOURITE.value,
            "default": IconType.DEFAULT.value,
        }

    def load_playlists(self) -> None:
        """
        Loads playlists into the widget.
        Clears the current playlist widget and populates it with playlists from the database.
        """
        self.playlist_widget.clear()
        playlists = self.db_manager.get_playlists()
        self.playlist_widget.addItems(playlists)

    def load_playlist(self, playlist: str, list_widget: QListWidget) -> None:
        """
        Loads songs from the selected playlist into the specified widget.

        Args:
            playlist (str): Name of the playlist.
            list_widget (QListWidget): Widget for displaying songs.
        """
        list_widget.clear()
        songs = self.db_manager.fetch_all_songs(f'"{playlist}"')
        icon_path = self.icon_config.get(playlist, self.icon_config["default"])
        for song in songs:
            item = QListWidgetItem(QIcon(icon_path), os.path.basename(song))
            item.setData(Qt.ItemDataRole.UserRole, song)
            list_widget.addItem(item)

    def select_playlist(self, parent_widget: QListWidget) -> tuple:
        """
        Displays a playlist selection dialog and returns the selected name.

        Args:
            parent_widget (QListWidget): Parent widget for the dialog.

        Returns:
            tuple: (playlist, ok) where playlist is the selected playlist name
                  and ok is a boolean indicating if selection was made.
        """
        playlists = self.db_manager.get_playlists()
        if "favourites" in playlists:
            playlists.remove("favourites")
        playlists.insert(0, "--Click to Select--")

        playlist, ok = QInputDialog.getItem(
            parent_widget,
            "Add song to playlist",
            "Choose the desired playlist:",
            playlists,
            0,  # Индекс первого элемента
            False,  # `editable=False`, чтобы пользователь не вводил свой текст
        )

        return playlist, ok

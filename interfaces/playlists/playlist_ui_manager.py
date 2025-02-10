import os

from PyQt5.QtWidgets import QListWidget, QInputDialog, QMessageBox, QListWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from interfaces.interfaces import IPlaylistUIManager


class PlaylistUIManager(IPlaylistUIManager):
    """
    Реализация IPlaylistUIManager для управления отображением плейлистов.
    Этот класс получает только необходимые виджеты (например, виджет для списка плейлистов)
    и работает независимо от остального главного окна.
    """

    def __init__(self, playlist_widget: QListWidget, db_manager):
        """
        :param playlist_widget: Виджет, в который будут загружаться имена плейлистов.
        :param db_manager: Объект, реализующий операции с базой данных для плейлистов.
        """
        self.playlist_widget = playlist_widget
        self.db_manager = db_manager

    def load_playlists(self) -> None:
        """Загружает плейлисты в виджет."""
        self.playlist_widget.clear()
        playlists = self.db_manager.get_playlists()
        self.playlist_widget.addItems(playlists)

    def load_playlist(self, playlist: str, list_widget: QListWidget) -> None:
        """
        Загружает песни выбранного плейлиста в указанный виджет.
        :param playlist: Имя плейлиста.
        :param list_widget: Виджет для отображения песен.
        """
        list_widget.clear()
        songs = self.db_manager.fetch_all_songs(f'"{playlist}"')
        for song in songs:
            icon = QIcon(":/img/utils/images/like.png") if playlist == "favourites" else QIcon(":/img/utils/images/MusicListItem.png")
            item = QListWidgetItem(icon, os.path.basename(song))
            item.setData(Qt.UserRole, song)
            list_widget.addItem(item)

    def refresh_playlists(self):
        self.load_playlists_into_widget()

    def select_playlist(self, parent_widget: QListWidget) -> tuple:
        """
        Отображает диалог выбора плейлиста и возвращает выбранное имя.
        :param parent_widget: Родительский виджет для диалога.
        :return: (playlist, ok)
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

    def check_list_not_empty(
        self, list_widget: QListWidget, message: str = "No songs in the list!"
    ) -> bool:
        if not list_widget or list_widget.count() == 0:
            QMessageBox.information(None, "Warning", message)
            return False
        return True

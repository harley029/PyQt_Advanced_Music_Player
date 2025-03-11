# test_utils.py
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QListWidget


def create_mock_ui_provider():
    """
    Создаёт мок для ui_provider с виджетами favourites и loaded_songs.
    """
    ui_provider = MagicMock()
    favourites_widget = MagicMock(spec=QListWidget)
    loaded_songs_widget = MagicMock(spec=QListWidget)
    ui_provider.get_favourites_widget.return_value = favourites_widget
    ui_provider.get_loaded_songs_widget.return_value = loaded_songs_widget
    return ui_provider, favourites_widget, loaded_songs_widget


def create_mock_music_controller(current_song="song.mp3"):
    """
    Создаёт мок музыкального контроллера с настроенным media_player.
    """
    music_controller = MagicMock()
    media_player = MagicMock()
    media = MagicMock()
    media.canonicalUrl.return_value.toLocalFile.return_value = current_song
    media_player.media.return_value = media
    music_controller.media_player.return_value = media_player
    return music_controller

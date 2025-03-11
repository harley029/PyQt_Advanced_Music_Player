import os
import sys
from unittest.mock import MagicMock

import pytest

from PyQt5.QtWidgets import QListWidget, QApplication
from PyQt5.QtCore import Qt

from interfaces.playlists.playlist_ui_manager import PlaylistUIManager, IconType


@pytest.fixture(scope="session", autouse=True)
def app():
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    return application


def test_playlist_ui_manager_init_default():
    # Создаем мок для QListWidget и для db_manager (достаточно задать метод get_playlists)
    mock_playlist_widget = MagicMock(spec=QListWidget)
    mock_db_manager = MagicMock()
    # Создаем экземпляр без явного icon_config
    manager = PlaylistUIManager(mock_playlist_widget, mock_db_manager)
    # Проверяем, что поля установлены корректно
    assert manager.playlist_widget is mock_playlist_widget
    assert manager.db_manager is mock_db_manager
    # Если не передали icon_config, должен использоваться словарь по умолчанию
    default_config = {
        "favourites": IconType.FAVOURITE.value,
        "default": IconType.DEFAULT.value,
    }
    assert manager.icon_config == default_config


def test_playlist_ui_manager_init_custom_icon_config():
    mock_playlist_widget = MagicMock(spec=QListWidget)
    mock_db_manager = MagicMock()
    custom_config = {"special": "icon_path.png"}
    manager = PlaylistUIManager(
        mock_playlist_widget, mock_db_manager, icon_config=custom_config
    )
    assert manager.icon_config == custom_config


def test_load_playlists():
    # Мокаем QListWidget и db_manager
    mock_playlist_widget = MagicMock(spec=QListWidget)
    mock_db_manager = MagicMock()
    playlists = ["playlist1", "playlist2"]
    mock_db_manager.get_playlists.return_value = playlists

    manager = PlaylistUIManager(mock_playlist_widget, mock_db_manager)
    manager.load_playlists()

    # Проверяем, что сначала очищается виджет, затем добавляются плейлисты
    mock_playlist_widget.clear.assert_called_once()
    mock_playlist_widget.addItems.assert_called_once_with(playlists)


def test_load_playlist():
    # Создаем моки для list_widget и db_manager
    mock_list_widget = MagicMock(spec=QListWidget)
    mock_db_manager = MagicMock()
    # Предположим, что в базе хранятся пути к песням
    songs = ["/music/song1.mp3", "/music/song2.mp3"]
    playlist_name = "my_playlist"
    mock_db_manager.fetch_all_songs.return_value = songs

    manager = PlaylistUIManager(None, mock_db_manager)
    manager.load_playlist(playlist_name, mock_list_widget)

    mock_list_widget.clear.assert_called_once()
    mock_db_manager.fetch_all_songs.assert_called_once_with(f'"{playlist_name}"')
    assert mock_list_widget.addItem.call_count == len(songs)
    calls = mock_list_widget.addItem.call_args_list
    for call_obj, song in zip(calls, songs):
        added_item = call_obj[0][0]
        expected_text = os.path.basename(song)
        # Предполагаем, что созданный QListWidgetItem хранит текст, доступный через метод text()
        assert added_item.text() == expected_text
        assert added_item.data(Qt.UserRole) == song


def test_select_playlist(monkeypatch):
    mock_parent_widget = MagicMock(spec=QListWidget)
    mock_db_manager = MagicMock()
    playlists = ["favourites", "playlist1", "playlist2"]
    mock_db_manager.get_playlists.return_value = playlists.copy()

    manager = PlaylistUIManager(None, mock_db_manager)

    def fake_get_item(parent, title, label, items, current, editable):
        assert items[0] == "--Click to Select--"
        assert "favourites" not in items
        return "playlist1", True

    monkeypatch.setattr("PyQt5.QtWidgets.QInputDialog.getItem", fake_get_item)
    result, ok = manager.select_playlist(mock_parent_widget)
    assert result == "playlist1"
    assert ok is True

import os
import sys
from unittest.mock import MagicMock

import pytest

from PyQt5.QtWidgets import QListWidget, QApplication
from PyQt5.QtCore import Qt

from interfaces.playlists.playlist_ui_manager import PlaylistUIManager, IconType


@pytest.fixture(scope="session", autouse=True)
def app():
    """
    Create and return a QApplication instance for the test session.

    This fixture ensures that a Qt application exists for the duration of the tests.
    If an application already exists, it reuses that instance; otherwise, it creates a new one.

    Returns:
        QApplication: The Qt application instance.
    """
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    return application


def test_playlist_ui_manager_init_default():
    """
    Test the initialization of PlaylistUIManager with default settings.

    This test verifies that the PlaylistUIManager correctly initializes with
    the provided playlist widget and database manager, and sets up the default
    icon configuration.
    """
    mock_playlist_widget = MagicMock(spec=QListWidget)
    mock_db_manager = MagicMock()
    manager = PlaylistUIManager(mock_playlist_widget, mock_db_manager)
    assert manager.playlist_widget is mock_playlist_widget
    assert manager.db_manager is mock_db_manager
    default_config = {
        "favourites": IconType.FAVOURITE.value,
        "default": IconType.DEFAULT.value,
    }
    assert manager.icon_config == default_config


def test_playlist_ui_manager_init_custom_icon_config():
    """
    Test the initialization of PlaylistUIManager with a custom icon configuration.

    This test verifies that when a custom icon configuration is provided,
    the PlaylistUIManager uses it instead of the default configuration.
    """
    mock_playlist_widget = MagicMock(spec=QListWidget)
    mock_db_manager = MagicMock()
    custom_config = {"special": "icon_path.png"}
    manager = PlaylistUIManager(
        mock_playlist_widget, mock_db_manager, icon_config=custom_config
    )
    assert manager.icon_config == custom_config


def test_load_playlists():
    """
    Test the load_playlists method of PlaylistUIManager.

    This test ensures that the method correctly retrieves playlists from the database,
    clears the playlist widget, and populates it with the retrieved playlists.
    """
    mock_playlist_widget = MagicMock(spec=QListWidget)
    mock_db_manager = MagicMock()
    playlists = ["playlist1", "playlist2"]
    mock_db_manager.get_playlists.return_value = playlists
    manager = PlaylistUIManager(mock_playlist_widget, mock_db_manager)
    manager.load_playlists()
    mock_playlist_widget.clear.assert_called_once()
    mock_playlist_widget.addItems.assert_called_once_with(playlists)


def test_load_playlist():
    """
    Test the load_playlist method of PlaylistUIManager.

    This test verifies that the method correctly:
    1. Clears the provided list widget
    2. Fetches songs for the specified playlist from the database
    3. Adds each song to the list widget with the correct display text (filename)
    4. Sets the full path as user data for each item
    """
    mock_list_widget = MagicMock(spec=QListWidget)
    mock_db_manager = MagicMock()
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
        assert added_item.text() == expected_text
        assert added_item.data(Qt.UserRole) == song


def test_select_playlist(monkeypatch):
    """
    Test the select_playlist method of PlaylistUIManager.

    This test verifies that:
    1. The method correctly prepares the playlist selection dialog
    2. The 'favourites' playlist is excluded from the selection options
    3. A default item "--Click to Select--" is added to the beginning of the list
    4. The method correctly returns the selected playlist and status flag

    Args:
        monkeypatch: Pytest fixture used to replace the QInputDialog.getItem function
    """
    mock_parent_widget = MagicMock(spec=QListWidget)
    mock_db_manager = MagicMock()
    playlists = ["favourites", "playlist1", "playlist2"]
    mock_db_manager.get_playlists.return_value = playlists.copy()
    manager = PlaylistUIManager(None, mock_db_manager)

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def fake_get_item(parent, title, label, items, current, editable):
        assert items[0] == "--Click to Select--"
        assert "favourites" not in items
        return "playlist1", True

    monkeypatch.setattr("PyQt5.QtWidgets.QInputDialog.getItem", fake_get_item)
    result, ok = manager.select_playlist(mock_parent_widget)
    assert result == "playlist1"
    assert ok is True

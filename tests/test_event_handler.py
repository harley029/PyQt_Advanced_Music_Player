# test_event_handler.py
# pylint: disable=redefined-outer-name, duplicate-code

from sqlite3 import IntegrityError, OperationalError
from unittest.mock import MagicMock, patch

import pytest
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QMessageBox

from controllers.favourites_manager import FavouritesManager
from utils import messages as msg

from tests.test_utils import create_mock_music_controller, create_mock_ui_provider


@pytest.fixture
def mock_ui_provider():
    """
    Fixture that creates a mock UI provider for testing.

    Returns:
        tuple: A tuple containing:
            - mock UI provider
            - mock favourites widget
            - mock loaded songs widget
    """
    return create_mock_ui_provider()


@pytest.fixture
def mock_parent(mock_ui_provider):
    """
    Creates a mock parent object with the necessary attributes and methods for testing.

    This fixture sets up a mock parent controller with all the required components
    for testing the FavouritesManager class. It includes database management functions,
    UI components, music controller, and list widget providers.

    Args:
        mock_ui_provider: The mock UI provider fixture

    Returns:
        MagicMock: A mock parent controller object with the following attributes:
            - db_manager: Mock database manager with methods for song manipulation
            - ui_provider: Mock UI provider
            - list_widget_provider: Mock list widget provider with selection functions
            - music_controller: Mock music controller with media playback functions
            - loaded_songs_listWidget: Mock loaded songs list widget
            - favourites_listWidget: Mock favourites list widget
            - current_playlist: None (placeholder for playlist functionality)
    """
    ui_provider, favourites_widget, loaded_songs_widget = mock_ui_provider
    parent = MagicMock()
    parent.db_manager = MagicMock()
    parent.db_manager.fetch_all_songs.return_value = []
    parent.db_manager.add_song = MagicMock()
    parent.db_manager.delete_song = MagicMock()
    parent.db_manager.delete_all_songs = MagicMock()
    parent.ui_provider = ui_provider
    list_widget_provider = MagicMock()
    list_widget_provider.get_currently_selected_song.return_value = "song.mp3"
    parent.list_widget_provider = list_widget_provider
    parent.music_controller = create_mock_music_controller()
    parent.loaded_songs_listWidget = loaded_songs_widget
    parent.favourites_listWidget = favourites_widget
    parent.current_playlist = None
    return parent


@pytest.fixture
def fav_manager(mock_parent):
    """
    Creates a FavouritesManager instance for testing.

    This fixture instantiates a FavouritesManager with the mock parent controller,
    which is used to test the functionality of managing favorite songs.

    Args:
        mock_parent: The mock parent controller fixture

    Returns:
        FavouritesManager: An instance of FavouritesManager initialized with the mock parent
    """
    return FavouritesManager(mock_parent)


# --- Tests for load_favourites ---


def test_load_favourites_success(fav_manager):
    """
    Tests that load_favourites successfully clears the widget and adds songs from the database.

    This test verifies that the load_favourites method correctly:
    1. Clears the existing favorites widget
    2. Fetches songs from the database
    3. Adds each song to the favorites widget

    Args:
        fav_manager: The FavouritesManager fixture

    Returns:
        None

    Assertions:
        - The favorites widget's clear method is called once
        - fetch_all_songs is called once with the table name "favourites"
        - addItem is called once for each song in the database
    """
    songs = ["/music/song1.mp3", "/music/song2.mp3"]
    fav_manager.db_manager.fetch_all_songs.return_value = songs
    fav_manager.favourites_widget = MagicMock(spec=QListWidget)
    fav_manager.favourites_widget.clear = MagicMock()
    fav_manager.favourites_widget.addItem = MagicMock()

    fav_manager.load_favourites()

    fav_manager.favourites_widget.clear.assert_called_once()
    fav_manager.db_manager.fetch_all_songs.assert_called_once_with("favourites")
    assert fav_manager.favourites_widget.addItem.call_count == len(songs)


def test_load_favourites_db_error(fav_manager):
    """
    Tests that a database error during load_favourites is handled correctly.

    This test verifies that when fetch_all_songs raises an OperationalError,
    the error is caught and the show_critical method is called with an
    appropriate error message.

    Args:
        fav_manager: The FavouritesManager fixture

    Returns:
        None

    Assertions:
        - show_critical is called once
        - The error message contains the text from the original exception
    """
    error = OperationalError("DB error")
    fav_manager.db_manager.fetch_all_songs.side_effect = error
    fav_manager.favourites_widget = MagicMock(spec=QListWidget)
    with patch.object(fav_manager.messanger, "show_critical") as mock_show_critical:
        fav_manager.load_favourites()
        mock_show_critical.assert_called_once()
        assert "DB error" in mock_show_critical.call_args[0][2]


# --- Tests for add_to_favourites ---


def test_add_to_favourites_loaded_empty(fav_manager):
    """
    Tests that add_to_favourites doesn't proceed when the loaded songs list is empty.

    This test verifies that when check_list_not_empty returns False (indicating
    the loaded songs list is empty), the add_song method is not called.

    Args:
        fav_manager: The FavouritesManager fixture

    Returns:
        None

    Assertions:
        - add_song is not called when the loaded songs list is empty
    """
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=False,
    ):
        fav_manager.add_to_favourites()
        fav_manager.db_manager.add_song.assert_not_called()


def test_add_to_favourites_no_item_selected(fav_manager):
    """
    Tests that add_to_favourites doesn't proceed when no item is selected.

    This test verifies that when check_item_selected returns False (indicating
    no item is selected in the loaded songs list), the add_song method is not called.

    Args:
        fav_manager: The FavouritesManager fixture

    Returns:
        None

    Assertions:
        - add_song is not called when no item is selected
    """
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.favourites_manager.list_validator.check_item_selected",
            return_value=False,
        ):
            fav_manager.add_to_favourites()
            fav_manager.db_manager.add_song.assert_not_called()


def test_add_to_favourites_no_current_song(fav_manager, mock_parent):
    """
    Tests that add_to_favourites shows a warning when no song is selected.

    This test verifies that when get_currently_selected_song returns None
    (indicating no song is currently selected), the following occurs:
    1. add_song is not called
    2. show_warning is called with the appropriate "no song selected" message

    Args:
        fav_manager: The FavouritesManager fixture
        mock_parent: The mock parent controller fixture

    Returns:
        None

    Assertions:
        - add_song is not called
        - show_warning is called once with the correct message
    """
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.favourites_manager.list_validator.check_item_selected",
            return_value=True,
        ):
            mock_parent.list_widget_provider.get_currently_selected_song.return_value = (
                None
            )
            with patch.object(
                fav_manager.messanger, "show_warning"
            ) as mock_show_warning:
                fav_manager.add_to_favourites()
                fav_manager.db_manager.add_song.assert_not_called()
                mock_show_warning.assert_called_once()
                assert msg.MSG_NO_SONG_SEL in mock_show_warning.call_args[0][2]


def test_add_to_favourites_success(fav_manager):
    """
    Tests that add_to_favourites successfully adds a song to favorites.

    This test verifies that when all conditions are met (non-empty list, item selected,
    valid song path), the add_song method is called with the correct parameters.

    Args:
        fav_manager: The FavouritesManager fixture

    Returns:
        None

    Assertions:
        - add_song is called once with the table name "favourites" and the song path
    """
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.favourites_manager.list_validator.check_item_selected",
            return_value=True,
        ):
            fav_manager.db_manager.add_song.side_effect = None
            fav_manager.add_to_favourites()
            fav_manager.db_manager.add_song.assert_called_once_with(
                "favourites", "song.mp3"
            )


def test_add_to_favourites_integrity_error(fav_manager):
    """
    Tests that add_to_favourites handles duplicate songs correctly.

    This test verifies that when add_song raises an IntegrityError (indicating
    the song already exists in favorites), the following occurs:
    1. The error is caught
    2. show_warning is called with the appropriate "song already exists" message

    Args:
        fav_manager: The FavouritesManager fixture

    Returns:
        None

    Assertions:
        - show_warning is called once with the correct message
    """
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.favourites_manager.list_validator.check_item_selected",
            return_value=True,
        ):
            fav_manager.db_manager.add_song.side_effect = IntegrityError("duplicate")
            with patch.object(
                fav_manager.messanger, "show_warning"
            ) as mock_show_warning:
                fav_manager.add_to_favourites()
                mock_show_warning.assert_called_once()
                assert msg.MSG_FAV_EXIST in mock_show_warning.call_args[0][2]


def test_add_to_favourites_operational_error(fav_manager):
    """
    Tests that add_to_favourites handles database errors correctly.

    This test verifies that when add_song raises an OperationalError (indicating
    a database error), the following occurs:
    1. The error is caught
    2. show_critical is called with an error message containing the original error text

    Args:
        fav_manager: The FavouritesManager fixture

    Returns:
        None

    Assertions:
        - show_critical is called once with an error message containing the original error text
    """
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.favourites_manager.list_validator.check_item_selected",
            return_value=True,
        ):
            error = OperationalError("op error")
            fav_manager.db_manager.add_song.side_effect = error
            with patch.object(
                fav_manager.messanger, "show_critical"
            ) as mock_show_critical:
                fav_manager.add_to_favourites()
                mock_show_critical.assert_called_once()
                assert "op error" in mock_show_critical.call_args[0][2]


# --- Tests for remove_selected_favourite ---


def test_remove_selected_favourite_empty_list(fav_manager, mock_parent):
    """
    Tests that remove_selected_favourite does nothing when the favorites list is empty.

    This test verifies that when check_list_not_empty returns False (indicating
    the favorites list is empty), no removal operations are performed.

    Args:
        fav_manager: The FavouritesManager fixture
        mock_parent: The mock parent controller fixture

    Returns:
        None

    Assertions:
        - stop_song is not called
        - delete_song is not called
    """
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=False,
    ):
        fav_widget = MagicMock(spec=QListWidget)
        fav_widget.count.return_value = 0
        fav_manager.favourites_widget = fav_widget
        fav_manager.remove_selected_favourite()
        mock_parent.music_controller.stop_song.assert_not_called()
        fav_manager.db_manager.delete_song.assert_not_called()


def test_remove_selected_favourite_no_selection(fav_manager, mock_parent):
    """
    Tests that remove_selected_favourite does nothing when no item is selected.

    This test verifies that when check_item_selected returns False (indicating
    no item is selected in the favorites list), no removal operations are performed.

    Args:
        fav_manager: The FavouritesManager fixture
        mock_parent: The mock parent controller fixture

    Returns:
        None

    Assertions:
        - stop_song is not called
        - delete_song is not called
    """
    with patch(
        "controllers.favourites_manager.list_validator.check_item_selected",
        return_value=False,
    ):
        fav_widget = MagicMock(spec=QListWidget)
        fav_widget.count.return_value = 1
        fav_manager.favourites_widget = fav_widget
        fav_manager.remove_selected_favourite()
        mock_parent.music_controller.stop_song.assert_not_called()
        fav_manager.db_manager.delete_song.assert_not_called()


def test_remove_selected_favourite_not_playing(fav_manager, mock_parent):
    """
    Tests that stop_song is not called if the deleted song is not currently playing.

    This test verifies that when a user removes a song from favorites that is not
    currently playing, the player does not stop playback but still removes the song
    from both the UI list and the database.

    Args:
        fav_manager: Mock of the FavouritesManager instance being tested
        mock_parent: Mock of the parent controller that contains the music_controller

    Assertions:
        - stop_song is not called
        - delete_song is called once with correct parameters
        - takeItem is called once to remove the item from the widget
    """
    fav_widget = MagicMock(spec=QListWidget)
    fav_widget.count.return_value = 1
    item = MagicMock(spec=QListWidgetItem)
    item.data.return_value = "song.mp3"
    fav_widget.item.return_value = item
    fav_widget.currentRow.return_value = 0
    fav_manager.favourites_widget = fav_widget
    with patch.object(
        fav_manager, "_get_current_playing_song", return_value="other_song.mp3"
    ):
        with patch(
            "controllers.favourites_manager.list_validator.check_list_not_empty",
            return_value=True,
        ):
            with patch(
                "controllers.favourites_manager.list_validator.check_item_selected",
                return_value=True,
            ):
                fav_manager.remove_selected_favourite()
    mock_parent.music_controller.stop_song.assert_not_called()
    fav_manager.db_manager.delete_song.assert_called_once_with("favourites", "song.mp3")
    fav_widget.takeItem.assert_called_once()


def test_remove_selected_favourite_playing_and_next(fav_manager, mock_parent):
    """
    Tests that when removing a currently playing song, playback stops and then
    switches to the next available song.

    This test ensures that when a user removes the song that is currently playing
    from favorites, the player stops the current song, removes it from both the UI
    list and database, and then automatically begins playing the next available song.

    Args:
        fav_manager: Mock of the FavouritesManager instance being tested
        mock_parent: Mock of the parent controller that contains the music_controller

    Assertions:
        - stop_song is called once
        - delete_song is called once with correct parameters
        - takeItem is called once to remove the item from the widget
        - play_song is called once to play the next song
    """
    fav_widget = MagicMock(spec=QListWidget)
    fav_widget.count.side_effect = lambda: 2 if fav_widget.count.call_count <= 1 else 1
    item = MagicMock(spec=QListWidgetItem)
    item.data.return_value = "song.mp3"
    fav_widget.item.side_effect = lambda i: item
    fav_widget.currentRow.return_value = 0
    fav_manager.favourites_widget = fav_widget
    with patch.object(
        fav_manager, "_get_current_playing_song", return_value="song.mp3"
    ):
        with patch(
            "controllers.favourites_manager.list_validator.check_list_not_empty",
            return_value=True,
        ):
            with patch(
                "controllers.favourites_manager.list_validator.check_item_selected",
                return_value=True,
            ):
                with patch.object(
                    mock_parent.music_controller, "stop_song"
                ) as mock_stop:
                    with patch.object(
                        mock_parent.music_controller, "play_song"
                    ) as mock_play:
                        fav_manager.remove_selected_favourite()
                        mock_stop.assert_called_once()
                        fav_manager.db_manager.delete_song.assert_called_once_with(
                            "favourites", "song.mp3"
                        )
                        fav_widget.takeItem.assert_called_once()
                        mock_play.assert_called_once()


def test_remove_selected_favourite_db_error(fav_manager):
    """
    Tests error handling when database operation fails during favorite song removal.

    This test verifies that when an OperationalError occurs during the database deletion
    operation, the application shows a critical error message to the user containing
    the error details.

    Args:
        fav_manager: Mock of the FavouritesManager instance being tested

    Assertions:
        - show_critical is called once with the error message
        - Error message contains the text from the OperationalError
    """
    fav_widget = MagicMock(spec=QListWidget)
    fav_widget.count.return_value = 1
    item = MagicMock(spec=QListWidgetItem)
    item.data.return_value = "song.mp3"
    fav_widget.item.return_value = item
    fav_widget.currentRow.return_value = 0
    fav_manager.favourites_widget = fav_widget
    error = OperationalError("DB delete error")
    fav_manager.db_manager.delete_song.side_effect = error
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.favourites_manager.list_validator.check_item_selected",
            return_value=True,
        ):
            with patch.object(
                fav_manager.messanger, "show_critical"
            ) as mock_show_critical:
                fav_manager.remove_selected_favourite()
                mock_show_critical.assert_called_once()
                assert "DB delete error" in mock_show_critical.call_args[0][2]


# --- Tests for clear_favourites ---


def test_clear_favourites_list_empty(fav_manager):
    """
    Tests that clear_favourites doesn't attempt to clear an already empty list.

    This test verifies that when the favorites list is empty (check_list_not_empty returns False),
    the clear_favourites method exits early without attempting to clear the list or interact
    with the database.

    Args:
        fav_manager: Mock of the FavouritesManager instance being tested

    Assertions:
        - favourites_widget.clear() is not called
    """
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=False,
    ):
        fav_manager.favourites_widget = MagicMock(spec=QListWidget)
        fav_manager.clear_favourites()
        fav_manager.favourites_widget.clear.assert_not_called()


def test_clear_favourites_no_confirmation(fav_manager, mock_parent):
    """
    Tests that clear_favourites respects user cancellation in the confirmation dialog.

    This test ensures that when a user cancels the clear operation in the confirmation
    dialog (returns QMessageBox.No), no changes are made to the favorites list or database.

    Args:
        fav_manager: Mock of the FavouritesManager instance being tested
        mock_parent: Mock of the parent controller that contains the music_controller

    Assertions:
        - stop_song is not called
        - favourites_widget.clear() is not called
        - delete_all_songs is not called
    """
    fav_widget = MagicMock(spec=QListWidget)
    fav_widget.count.return_value = 2
    fav_manager.favourites_widget = fav_widget
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch.object(
            fav_manager.messanger, "show_question", return_value=QMessageBox.No
        ):
            fav_manager.clear_favourites()
            mock_parent.music_controller.stop_song.assert_not_called()
            fav_widget.clear.assert_not_called()
            fav_manager.db_manager.delete_all_songs.assert_not_called()


def test_clear_favourites_success(fav_manager, mock_parent):
    """
    Tests successful clearing of the favorites list with user confirmation.

    This test verifies that when a user confirms clearing the favorites list:
    1. If a song from the list is currently playing, it stops playback
    2. The favorites widget is cleared
    3. All songs are deleted from the favorites database table

    Args:
        fav_manager: Mock of the FavouritesManager instance being tested
        mock_parent: Mock of the parent controller that contains the music_controller

    Assertions:
        - stop_song is called once (when a favorites song is playing)
        - favourites_widget.clear() is called once
        - delete_all_songs is called once with the "favourites" table
    """
    fav_widget = MagicMock(spec=QListWidget)
    fav_widget.count.return_value = 2
    item = MagicMock(spec=QListWidgetItem)
    item.data.return_value = "song.mp3"
    fav_widget.item.side_effect = lambda i: item
    fav_manager.favourites_widget = fav_widget
    with patch.object(
        fav_manager, "_get_current_playing_song", return_value="song.mp3"
    ):
        with patch.object(
            fav_manager.messanger, "show_question", return_value=QMessageBox.Yes
        ):
            fav_manager.clear_favourites()
    mock_parent.music_controller.stop_song.assert_called_once()
    fav_widget.clear.assert_called_once()
    fav_manager.db_manager.delete_all_songs.assert_called_once_with("favourites")


def test_clear_favourites_db_error(fav_manager):
    """
    Tests error handling when database operation fails during clear favorites operation.

    This test verifies that when an OperationalError occurs during the database operation
    to delete all songs, the application shows a critical error message to the user
    containing the error details.

    Args:
        fav_manager: Mock of the FavouritesManager instance being tested

    Assertions:
        - show_critical is called once with an error message
        - Error message contains the text from the OperationalError
    """
    fav_widget = MagicMock(spec=QListWidget)
    fav_widget.count.return_value = 2
    fav_manager.favourites_widget = fav_widget
    error = OperationalError("Clear error")
    fav_manager.db_manager.delete_all_songs.side_effect = error
    with patch("PyQt5.QtWidgets.QMessageBox.question", return_value=QMessageBox.Yes):
        with patch(
            "controllers.favourites_manager.list_validator.check_list_not_empty",
            return_value=True,
        ):
            with patch.object(
                fav_manager.messanger, "show_critical"
            ) as mock_show_critical:
                fav_manager.clear_favourites()
                mock_show_critical.assert_called_once()
                assert "Clear error" in mock_show_critical.call_args[0][2]


# --- Tests for add_all_to_favourites ---


def test_add_all_to_favourites_success(fav_manager, mock_parent):
    """
    Tests successful addition of all loaded songs to favorites.

    This test verifies that the add_all_to_favourites method correctly:
    1. Retrieves all songs from the loaded_songs_widget
    2. Adds each song to the favorites database
    3. Shows an information message with the count of successfully added songs

    Args:
        fav_manager: Mock of the FavouritesManager instance being tested
        mock_parent: Mock of the parent controller with UI provider

    Assertions:
        - db_manager.add_song is called for each song in the loaded list
        - show_info is called with a message containing the number of added songs
    """
    loaded_widget = MagicMock(spec=QListWidget)
    loaded_widget.count.return_value = 3
    item1 = MagicMock(spec=QListWidgetItem)
    item2 = MagicMock(spec=QListWidgetItem)
    item3 = MagicMock(spec=QListWidgetItem)
    item1.data.return_value = "/music/song1.mp3"
    item2.data.return_value = "/music/song2.mp3"
    item3.data.return_value = "/music/song3.mp3"
    loaded_widget.item.side_effect = lambda i: [item1, item2, item3][i]
    mock_parent.ui_provider.get_loaded_songs_widget.return_value = loaded_widget
    fav_manager.loaded_songs_widget = loaded_widget
    fav_manager.db_manager.add_song.side_effect = lambda table, song: None
    with patch.object(fav_manager.messanger, "show_info") as mock_show_info:
        fav_manager.add_all_to_favourites()
        assert fav_manager.db_manager.add_song.call_count == 3
        mock_show_info.assert_called_once()
        args, _ = mock_show_info.call_args
        assert "3" in args[2]


def test_add_all_to_favourites_operational_error(fav_manager, mock_parent):
    """
    Tests error handling when database operation fails during add all to favorites.

    This test verifies that when an OperationalError occurs during the database operation
    to add songs, the application shows a critical error message to the user containing
    the error details.

    Args:
        fav_manager: Mock of the FavouritesManager instance being tested
        mock_parent: Mock of the parent controller with UI provider

    Assertions:
        - show_critical is called once with an error message
        - Error message contains the text from the OperationalError
    """
    loaded_widget = MagicMock(spec=QListWidget)
    loaded_widget.count.return_value = 1
    item = MagicMock(spec=QListWidgetItem)
    item.data.return_value = "/music/song1.mp3"
    loaded_widget.item.return_value = item
    mock_parent.ui_provider.get_loaded_songs_widget.return_value = loaded_widget
    fav_manager.loaded_songs_widget = loaded_widget
    error = OperationalError("Add all error")
    fav_manager.db_manager.add_song.side_effect = error
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch.object(fav_manager.messanger, "show_critical") as mock_show_critical:
            fav_manager.add_all_to_favourites()
            mock_show_critical.assert_called_once()
            assert "Add all error" in mock_show_critical.call_args[0][2]


def test_add_all_to_favourites_integrity_issues(fav_manager, mock_parent):
    """
    Tests handling of integrity errors when adding duplicates to favorites.

    This test verifies that when some songs cause IntegrityError (likely because they
    already exist in favorites), those songs are skipped but the operation continues
    with the remaining songs. The information message should reflect only the count
    of successfully added songs.

    Args:
        fav_manager: Mock of the FavouritesManager instance being tested
        mock_parent: Mock of the parent controller with UI provider

    Assertions:
        - db_manager.add_song is called for each song in the loaded list (3 times)
        - show_info is called with a message containing the number of successfully added songs (1)
    """
    loaded_widget = MagicMock(spec=QListWidget)
    loaded_widget.count.return_value = 3
    item1 = MagicMock(spec=QListWidgetItem)
    item2 = MagicMock(spec=QListWidgetItem)
    item3 = MagicMock(spec=QListWidgetItem)
    item1.data.return_value = "/music/song1.mp3"
    item2.data.return_value = "/music/song2.mp3"
    item3.data.return_value = "/music/song3.mp3"
    loaded_widget.item.side_effect = lambda i: [item1, item2, item3][i]
    mock_parent.ui_provider.get_loaded_songs_widget.return_value = loaded_widget
    fav_manager.loaded_songs_widget = loaded_widget

    def add_song_side_effect(table, song):
        if song == "/music/song1.mp3":
            return
        raise IntegrityError("Already exists")

    fav_manager.db_manager.add_song.side_effect = add_song_side_effect

    with patch.object(fav_manager.messanger, "show_info") as mock_show_info:
        fav_manager.add_all_to_favourites()
        assert fav_manager.db_manager.add_song.call_count == 3
        mock_show_info.assert_called_once()
        args, _ = mock_show_info.call_args
        assert "1" in args[2]


# --- Test for _get_current_playing_song ---


def test_get_current_playing_song(fav_manager, mock_parent):
    """
    Tests the internal method to retrieve the current playing song's file path.

    This test verifies that the _get_current_playing_song method correctly accesses
    the media player's current media object and extracts the local file path of
    the currently playing song.

    Args:
        fav_manager: Mock of the FavouritesManager instance being tested
        mock_parent: Mock of the parent controller containing the music_controller

    Returns:
        None

    Assertions:
        - The returned value matches the expected local file path ("current_song.mp3")
    """
    media_player = MagicMock()
    media = MagicMock()
    media.canonicalUrl.return_value.toLocalFile.return_value = "current_song.mp3"
    media_player.media.return_value = media
    mock_parent.music_controller.media_player.return_value = media_player
    result = fav_manager._get_current_playing_song()
    assert result == "current_song.mp3"

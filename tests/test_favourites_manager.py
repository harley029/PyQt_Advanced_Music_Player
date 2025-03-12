# pylint: disable=redefined-outer-name, duplicate-code

from sqlite3 import IntegrityError, OperationalError
from unittest.mock import MagicMock, patch

import pytest
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QMessageBox

from controllers.favourites_manager import FavouritesManager
from utils import messages as msg

from tests.test_utils import create_mock_ui_provider, create_mock_music_controller


@pytest.fixture
def mock_ui_provider():
    """Fixture to create a mock UI provider for testing.

    Returns:
        tuple: A tuple containing:
            - ui_provider (MagicMock): Mock of the UIProvider class
            - favourites_widget (MagicMock): Mock of the favourites QListWidget
            - loaded_songs_widget (MagicMock): Mock of the loaded songs QListWidget
    """
    return create_mock_ui_provider()


@pytest.fixture
def mock_parent(mock_ui_provider):
    """Creates a mock parent object with necessary attributes for testing FavouritesManager.

    Args:
        mock_ui_provider (tuple): The result of mock_ui_provider fixture containing UI mocks

    Returns:
        MagicMock: A mock parent object with the following configured attributes:
            - db_manager: Mock with methods for database operations
            - ui_provider: The mock UI provider from the fixture
            - list_widget_provider: Mock with method to get currently selected song
            - music_controller: Mock of the music controller component
            - loaded_songs_listWidget: Mock list widget for loaded songs
            - favourites_listWidget: Mock list widget for favourites
            - current_playlist: Set to None initially
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
    """Creates a favourites manager instance with mocked dependencies.

    Args:
        mock_parent (MagicMock): Mock parent object with required attributes

    Returns:
        FavouritesManager: An instance of FavouritesManager initialized with the mock parent
    """
    return FavouritesManager(mock_parent)


@pytest.fixture(autouse=True)
def patch_message_manager():
    """Patches MessageManager methods to prevent real dialog windows during tests.

    This fixture is automatically applied to all tests in this module. It patches
    the MessageManager's show_warning, show_critical, show_info, and show_question
    methods to avoid showing actual UI dialogs during test execution.

    Returns:
        dict: A dictionary containing the mocked message manager methods:
            - show_warning: Mock for the warning dialog
            - show_critical: Mock for the critical error dialog
            - show_info: Mock for the information dialog
    """
    with patch(
        "controllers.favourites_manager.MessageManager.show_warning"
    ) as show_warning, patch(
        "controllers.favourites_manager.MessageManager.show_critical"
    ) as show_critical, patch(
        "controllers.favourites_manager.MessageManager.show_info"
    ) as show_info, patch(
        "controllers.favourites_manager.MessageManager.show_question",
        return_value=QMessageBox.Yes,
    ):
        yield {
            "show_warning": show_warning,
            "show_critical": show_critical,
            "show_info": show_info,
        }


# -------------------- Tests for FavouritesManager ------------------------


def test_load_favourites_success(fav_manager):
    """Tests that load_favourites properly populates the favourites widget.

    This test verifies that the load_favourites method:
    1. Clears the existing favourites widget
    2. Retrieves songs from the database
    3. Adds each song to the favourites widget

    Args:
        fav_manager (FavouritesManager): A fixture providing the FavouritesManager instance

    Returns:
        None
    """
    fav_manager.db_manager.fetch_all_songs.return_value = [
        "/music/song1.mp3",
        "/music/song2.mp3",
    ]
    fav_manager.favourites_widget = MagicMock(spec=QListWidget)
    fav_manager.favourites_widget.clear = MagicMock()
    fav_manager.favourites_widget.addItem = MagicMock()
    fav_manager.load_favourites()
    fav_manager.favourites_widget.clear.assert_called_once()
    fav_manager.db_manager.fetch_all_songs.assert_called_once_with("favourites")
    assert fav_manager.favourites_widget.addItem.call_count == 2


def test_add_to_favourites_success(fav_manager, mock_parent):
    """Tests successful addition of a song to favourites.

    This test verifies that the add_to_favourites method correctly:
    1. Gets the currently selected song from the loaded songs widget
    2. Adds it to the favourites database table

    Args:
        fav_manager (FavouritesManager): A fixture providing the FavouritesManager instance
        mock_parent (MagicMock): A fixture providing the mock parent object

    Returns:
        None
    """
    loaded_widget = MagicMock(spec=QListWidget)
    loaded_widget.count.return_value = 1
    item = MagicMock(spec=QListWidgetItem)
    item.data.return_value = "song.mp3"
    loaded_widget.currentItem.return_value = item
    mock_parent.ui_provider.get_loaded_songs_widget.return_value = loaded_widget
    fav_manager.loaded_songs_widget = loaded_widget
    fav_manager.add_to_favourites()
    fav_manager.db_manager.add_song.assert_called_once_with("favourites", "song.mp3")


def test_add_to_favourites_no_selection(fav_manager, mock_parent):
    """Tests handling when no song is selected when adding to favourites.

    This test verifies that the add_to_favourites method:
    1. Detects when no song is selected
    2. Does not attempt to add a song to the database
    3. Shows an appropriate warning message

    Args:
        fav_manager (FavouritesManager): A fixture providing the FavouritesManager instance
        mock_parent (MagicMock): A fixture providing the mock parent object

    Returns:
        None
    """
    loaded_widget = MagicMock(spec=QListWidget)
    loaded_widget.count.return_value = 1
    loaded_widget.currentItem.return_value = None
    mock_parent.ui_provider.get_loaded_songs_widget.return_value = loaded_widget
    fav_manager.loaded_songs_widget = loaded_widget
    mock_parent.list_widget_provider.get_currently_selected_song.return_value = None

    with patch.object(fav_manager.messanger, "show_warning") as mock_show_warning:
        fav_manager.add_to_favourites()
        fav_manager.db_manager.add_song.assert_not_called()
        mock_show_warning.assert_called_once()
        assert msg.MSG_NO_SONG_SEL in mock_show_warning.call_args[0][2]


def test_remove_selected_favourite_success(fav_manager, mock_parent):
    """Tests successful removal of a selected favourite song.

    This test verifies that the remove_selected_favourite method correctly:
    1. Gets the selected song from the favourites widget
    2. Stops playback if the song is currently playing
    3. Removes the song from the database
    4. Removes the song from the favourites widget UI

    Args:
        fav_manager (FavouritesManager): A fixture providing the FavouritesManager instance
        mock_parent (MagicMock): A fixture providing the mock parent object

    Returns:
        None
    """
    fav_widget = MagicMock(spec=QListWidget)
    item = MagicMock(spec=QListWidgetItem)
    item.data.return_value = "song.mp3"
    fav_widget.count.return_value = 1
    fav_widget.item.return_value = item
    fav_widget.currentRow.return_value = 0
    fav_manager.favourites_widget = fav_widget

    with patch.object(
        fav_manager, "_get_current_playing_song", return_value="song.mp3"
    ):
        fav_manager.remove_selected_favourite()

    mock_parent.music_controller.stop_song.assert_called_once()
    fav_manager.db_manager.delete_song.assert_called_once_with("favourites", "song.mp3")
    fav_widget.takeItem.assert_called_once()


def test_remove_selected_favourite_empty_list(fav_manager, mock_parent):
    """Tests handling when trying to remove from an empty favourites list.

    This test verifies that the remove_selected_favourite method:
    1. Detects when the favourites list is empty
    2. Does not attempt any deletion operations

    Args:
        fav_manager (FavouritesManager): A fixture providing the FavouritesManager instance
        mock_parent (MagicMock): A fixture providing the mock parent object

    Returns:
        None
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
    """Tests handling when no favourite is selected for removal.

    This test verifies that the remove_selected_favourite method:
    1. Detects when no item is selected in the favourites list
    2. Does not attempt any deletion operations

    Args:
        fav_manager (FavouritesManager): A fixture providing the FavouritesManager instance
        mock_parent (MagicMock): A fixture providing the mock parent object

    Returns:
        None
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


def test_remove_selected_favourite_playing_and_next(fav_manager, mock_parent):
    """Tests removal of currently playing song with automatic next song playback.

    This test verifies that the remove_selected_favourite method:
    1. Detects when the deleted song is the currently playing one
    2. Stops playback of the current song
    3. Removes the song from the database and UI
    4. Automatically plays the next available song

    Args:
        fav_manager (FavouritesManager): A fixture providing the FavouritesManager instance
        mock_parent (MagicMock): A fixture providing the mock parent object

    Returns:
        None
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
    """Tests error handling when database deletion fails.

    This test verifies that the remove_selected_favourite method:
    1. Properly catches database operational errors
    2. Shows a critical error message with the error details

    Args:
        fav_manager (FavouritesManager): A fixture providing the FavouritesManager instance

    Returns:
        None
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


def test_clear_favourites_list_empty(fav_manager):
    """
    Tests that clear_favourites doesn't clear the list when it's empty.

    This test mocks the check_list_not_empty function to return False,
    simulating an empty favorites list. It then verifies that the
    clear method of the favourites_widget is not called.

    Args:
        fav_manager: The FavouritesManager instance under test

    Returns:
        None
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
    Tests that clear_favourites doesn't clear the list when user cancels confirmation.

    This test simulates a non-empty favorites list but the user selecting "No" in
    the confirmation dialog. It verifies that the list is not cleared, the current song
    is not stopped, and the database delete operation is not performed.

    Args:
        fav_manager: The FavouritesManager instance under test
        mock_parent: Mock of the parent controller with music_controller attribute

    Returns:
        None
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
    Tests that clear_favourites successfully clears the list when user confirms.

    This test simulates a non-empty favorites list with the user selecting "Yes" in
    the confirmation dialog. It verifies that if the currently playing song is in
    the favorites list, the song is stopped, the favorites widget is cleared, and
    all songs are deleted from the database.

    Args:
        fav_manager: The FavouritesManager instance under test
        mock_parent: Mock of the parent controller with music_controller attribute

    Returns:
        None
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
    Tests that clear_favourites handles database errors appropriately.

    This test simulates a database error occurring during the delete operation.
    It verifies that the error is caught and the show_critical method is called
    with an error message containing the original error text.

    Args:
        fav_manager: The FavouritesManager instance under test

    Returns:
        None

    Side Effects:
        Should display a critical error message to the user
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


def test_add_all_to_favourites_success(fav_manager, mock_parent):
    """
    Tests that add_all_to_favourites successfully adds all loaded songs to favorites.

    This test simulates a scenario where three songs are available in the loaded songs widget.
    It verifies that all songs are added to the database and an information message is displayed
    with the correct count of added songs.

    Args:
        fav_manager: The FavouritesManager instance under test
        mock_parent: Mock of the parent controller with ui_provider attribute

    Returns:
        None

    Side Effects:
        Should display an information message with the number of songs added
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
    Tests that add_all_to_favourites handles database operational errors appropriately.

    This test simulates a database operational error occurring during the add operation.
    It verifies that the error is caught and the show_critical method is called
    with an error message containing the original error text.

    Args:
        fav_manager: The FavouritesManager instance under test
        mock_parent: Mock of the parent controller with ui_provider attribute

    Returns:
        None

    Side Effects:
        Should display a critical error message to the user
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
    Tests that add_all_to_favourites handles integrity errors gracefully.

    This test simulates a scenario where multiple songs are being added but some
    already exist in the database (causing IntegrityError). It verifies that the
    operation continues despite these errors and an information message is displayed
    with the correct count of successfully added songs.

    Args:
        fav_manager: The FavouritesManager instance under test
        mock_parent: Mock of the parent controller with ui_provider attribute

    Returns:
        None

    Side Effects:
        Should display an information message with the number of successfully added songs
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


def test_get_current_playing_song(fav_manager, mock_parent):
    """
    Tests that _get_current_playing_song correctly retrieves the path of the currently playing song.

    This test mocks the media player and associated objects to simulate a currently
    playing song. It verifies that the method correctly extracts and returns the
    file path of the song.

    Args:
        fav_manager: The FavouritesManager instance under test
        mock_parent: Mock of the parent controller with music_controller attribute

    Returns:
        None

    Expected Result:
        The method should return the local file path of the currently playing song
    """
    media_player = MagicMock()
    media = MagicMock()
    media.canonicalUrl.return_value.toLocalFile.return_value = "current_song.mp3"
    media_player.media.return_value = media
    mock_parent.music_controller.media_player.return_value = media_player

    result = fav_manager._get_current_playing_song()
    assert result == "current_song.mp3"

from sqlite3 import IntegrityError, DatabaseError

from unittest.mock import MagicMock, patch
import pytest

from PyQt5.QtWidgets import QListWidget, QMessageBox

from interfaces.playlists.playlist_manager import PlaylistManager, PlaylistError
from utils import messages as msg


class TestPlaylistManager:
    @pytest.fixture
    def playlist_manager(self):
        """
        Create a PlaylistManager instance with mocked dependencies for testing.

        This fixture sets up a PlaylistManager with mocked database manager and UI components.
        All method calls on the mocked objects are replaced with MagicMock instances to avoid
        actual database operations or UI interactions during tests.

        Returns:
            PlaylistManager: A configured PlaylistManager instance with mock dependencies.
        """
        mock_db_manager = MagicMock()
        mock_playlist_widget = MagicMock(spec=QListWidget)
        playlist_manager = PlaylistManager(mock_db_manager, mock_playlist_widget)
        playlist_manager.ui_manager.load_playlists = MagicMock()
        playlist_manager.ui_manager.load_playlist = MagicMock()
        playlist_manager.ui_manager.select_playlist = MagicMock()
        playlist_manager.db_manager.get_playlists = MagicMock()
        playlist_manager.db_manager.create_playlist = MagicMock()
        playlist_manager.db_manager.delete_playlist = MagicMock()
        playlist_manager.db_manager.add_song_to_playlist = MagicMock()
        playlist_manager.messanger.show_info = MagicMock()
        playlist_manager.messanger.show_warning = MagicMock()
        playlist_manager.messanger.show_critical = MagicMock()
        playlist_manager.messanger.show_question = MagicMock()

        return playlist_manager

    @pytest.fixture
    def mock_parent(self):
        """
        Create a mock parent widget for testing.

        This fixture creates a mock parent widget with all the necessary attributes
        and methods that would be required by a PlaylistManager during tests, including
        list widgets, music controllers, and UI update methods.

        Returns:
            MagicMock: A mock parent widget with all required attributes.
        """
        parent = MagicMock()
        parent.loaded_songs_listWidget = MagicMock(spec=QListWidget)
        parent.playlists_listWidget = MagicMock(spec=QListWidget)
        parent.music_controller = MagicMock()
        parent.ui_updater = MagicMock()
        parent.switch_to_songs_tab = MagicMock()
        return parent

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_load_playlists_into_widget(self, mock_list_validator, playlist_manager):
        """
        Test that load_playlists_into_widget calls ui_manager.load_playlists.

        This test verifies that the load_playlists_into_widget method correctly delegates
        to the ui_manager's load_playlists method.

        Args:
            mock_list_validator: Mocked list_validator module.
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
        """
        playlist_manager.load_playlists_into_widget()
        playlist_manager.ui_manager.load_playlists.assert_called_once()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_load_playlist_into_widget_empty_list(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test load_playlist_into_widget behavior with an empty playlist list.

        Verifies that when the playlist list is empty, the validation is performed,
        and no playlist loading operations are attempted.

        Args:
            mock_list_validator: Mocked list_validator module.
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.
        """
        mock_list_validator.check_list_not_empty.return_value = False
        playlist_manager.load_playlist_into_widget(mock_parent)
        mock_list_validator.check_list_not_empty.assert_called_once_with(
            playlist_manager.list_widget, msg.MSG_NO_LSTS
        )
        playlist_manager.ui_manager.load_playlist.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_load_playlist_into_widget_no_selection(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test load_playlist_into_widget behavior when no playlist is selected.

        Verifies that when no playlist is selected, the appropriate validation is performed,
        and no playlist loading operations are attempted.

        Args:
            mock_list_validator: Mocked list_validator module.
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.
        """
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = False
        playlist_manager.load_playlist_into_widget(mock_parent)
        mock_list_validator.check_item_selected.assert_called_once_with(
            playlist_manager.list_widget, mock_parent, message=msg.MSG_NO_LST_SEL
        )
        playlist_manager.ui_manager.load_playlist.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_load_playlist_into_widget_success(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test successful execution of load_playlist_into_widget with a valid selection.

        Verifies that when a playlist is selected, the method correctly loads the playlist,
        switches to the songs tab, and updates the current playlist reference.

        Args:
            mock_list_validator: Mocked list_validator module.
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.
        """
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = True
        playlist_manager.list_widget.currentRow.return_value = 0
        mock_item = MagicMock()
        mock_item.text.return_value = "Test Playlist"
        playlist_manager.list_widget.item.return_value = mock_item

        playlist_manager.load_playlist_into_widget(mock_parent)

        playlist_manager.ui_manager.load_playlist.assert_called_once_with(
            "Test Playlist", mock_parent.loaded_songs_listWidget
        )
        mock_parent.switch_to_songs_tab.assert_called_once()
        assert mock_parent.current_playlist == "Test Playlist"

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_load_playlist_into_widget_database_error(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test load_playlist_into_widget handling of DatabaseError exceptions.

        Verifies that when a DatabaseError occurs during playlist loading, the method
        properly catches the exception and displays an appropriate error message.

        Args:
            mock_list_validator: Mocked list_validator module.
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.
        """
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = True
        playlist_manager.list_widget.currentRow.return_value = 0
        mock_item = MagicMock()
        mock_item.text.return_value = "Test Playlist"
        playlist_manager.list_widget.item.return_value = mock_item
        playlist_manager.ui_manager.load_playlist.side_effect = DatabaseError(
            "DB error"
        )

        playlist_manager.load_playlist_into_widget(mock_parent)

        playlist_manager.messanger.show_critical.assert_called_once_with(
            mock_parent, msg.TTL_ERR, "Database error while loading playlist: DB error"
        )

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_load_playlist_into_widget_playlist_error(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test load_playlist_into_widget handling of PlaylistError exceptions.

        Verifies that when a PlaylistError occurs during playlist loading, the method
        properly catches the exception and displays an appropriate error message.

        Args:
            mock_list_validator: Mocked list_validator module.
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.
        """
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = True
        playlist_manager.list_widget.currentRow.return_value = 0
        mock_item = MagicMock()
        mock_item.text.return_value = "Test Playlist"
        playlist_manager.list_widget.item.return_value = mock_item
        playlist_manager.ui_manager.load_playlist.side_effect = PlaylistError(
            "Playlist error"
        )

        playlist_manager.load_playlist_into_widget(mock_parent)

        playlist_manager.messanger.show_critical.assert_called_once_with(
            mock_parent, msg.TTL_ERR, "Playlist error: Playlist error"
        )

    def test_create_playlist_new(self, playlist_manager, mock_parent):
        """
        Test creating a new playlist with a unique name.

        Verifies that when creating a new playlist with a unique name, the method
        correctly creates the playlist, reloads the playlist UI, and returns the name.

        Args:
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.

        Returns:
            None
        """
        playlist_manager.db_manager.get_playlists.return_value = ["Existing Playlist"]
        with patch(
            "interfaces.playlists.playlist_manager.QInputDialog.getText",
            return_value=("New Playlist", True),
        ):
            result = playlist_manager.create_playlist(mock_parent)

        playlist_manager.db_manager.create_playlist.assert_called_once_with(
            "New Playlist"
        )
        playlist_manager.ui_manager.load_playlists.assert_called_once()
        assert result == "New Playlist"

    def test_create_playlist_cancel(self, playlist_manager, mock_parent):
        """
        Test create_playlist behavior when user cancels or provides an empty name.

        Verifies that when the user cancels the dialog or provides an empty playlist name,
        no playlist is created and the method returns None.

        Args:
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.

        Returns:
            None
        """
        playlist_manager.db_manager.get_playlists.return_value = ["Existing Playlist"]
        with patch(
            "interfaces.playlists.playlist_manager.QInputDialog.getText",
            return_value=("", False),
        ):
            result = playlist_manager.create_playlist(mock_parent)

        playlist_manager.db_manager.create_playlist.assert_not_called()
        assert result is None

    def test_create_playlist_value_error(self, playlist_manager, mock_parent):
        """
        Test create_playlist handling of ValueError exceptions.

        Verifies that when a ValueError occurs during playlist creation (e.g., due to
        invalid name), the method properly catches the exception and displays an
        appropriate error message.

        Args:
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.

        Returns:
            None
        """
        playlist_manager.db_manager.get_playlists.side_effect = ValueError(
            "Invalid name"
        )
        with patch(
            "interfaces.playlists.playlist_manager.QInputDialog.getText",
            return_value=("Invalid Playlist", True),
        ):
            result = playlist_manager.create_playlist(mock_parent)

        playlist_manager.messanger.show_critical.assert_called_once_with(
            mock_parent, msg.TTL_ERR, "Invalid playlist name: Invalid name"
        )
        assert result is None

    def test_create_playlist_database_error(self, playlist_manager, mock_parent):
        """
        Test create_playlist handling of DatabaseError exceptions.

        Verifies that when a DatabaseError occurs during playlist creation, the method
        properly catches the exception and displays an appropriate error message.

        Args:
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.

        Returns:
            None
        """
        playlist_manager.db_manager.get_playlists.return_value = ["Existing Playlist"]
        playlist_manager.db_manager.create_playlist.side_effect = DatabaseError(
            "DB error"
        )
        with patch(
            "interfaces.playlists.playlist_manager.QInputDialog.getText",
            return_value=("New Playlist", True),
        ):
            result = playlist_manager.create_playlist(mock_parent)

        playlist_manager.messanger.show_critical.assert_called_once_with(
            mock_parent, msg.TTL_ERR, "Database error while creating playlist: DB error"
        )
        assert result == "New Playlist"

    def test_create_playlist_replace_no(self, playlist_manager, mock_parent):
        """
        Test create_playlist behavior when user declines to replace an existing playlist.

        Verifies that when the user chooses not to replace an existing playlist with the same name,
        no playlist operations are performed and the method returns None.

        Args:
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.

        Returns:
            None
        """
        playlist_manager.db_manager.get_playlists.return_value = ["Existing Playlist"]
        with patch(
            "interfaces.playlists.playlist_manager.QInputDialog.getText",
            return_value=("Existing Playlist", True),
        ):
            playlist_manager.messanger.show_question.return_value = QMessageBox.No
            result = playlist_manager.create_playlist(mock_parent)

        playlist_manager.db_manager.delete_playlist.assert_not_called()
        playlist_manager.db_manager.create_playlist.assert_not_called()
        assert result is None

    def test_create_playlist_replace(self, playlist_manager, mock_parent):
        """
        Test create_playlist behavior when replacing an existing playlist.

        Verifies that when the user chooses to replace an existing playlist with the same name,
        the old playlist is deleted, a new one is created, the UI is updated, and the name is returned.

        Args:
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.

        Returns:
            None
        """
        playlist_manager.db_manager.get_playlists.return_value = ["Existing Playlist"]
        with patch(
            "interfaces.playlists.playlist_manager.QInputDialog.getText",
            return_value=("Existing Playlist", True),
        ):
            playlist_manager.messanger.show_question.return_value = QMessageBox.Yes
            result = playlist_manager.create_playlist(mock_parent)

        playlist_manager.db_manager.delete_playlist.assert_called_once_with(
            "Existing Playlist"
        )
        playlist_manager.db_manager.create_playlist.assert_called_once_with(
            "Existing Playlist"
        )
        playlist_manager.ui_manager.load_playlists.assert_called_once()
        assert result == "Existing Playlist"

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_remove_playlist_success(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test successful removal of a playlist.

        Verifies that when removing a valid playlist with confirmation, the method correctly
        stops any playing song, clears song info, deletes the playlist, updates the UI,
        and clears the current playlist reference.

        Args:
            mock_list_validator: Mocked list_validator module.
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.

        Returns:
            None
        """
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = True
        playlist_manager.list_widget.currentRow.return_value = 0
        mock_item = MagicMock()
        mock_item.text.return_value = "Test Playlist"
        playlist_manager.list_widget.item.return_value = mock_item
        mock_parent.current_playlist = "Test Playlist"
        playlist_manager.messanger.show_question.return_value = QMessageBox.Yes
        playlist_manager.list_widget.count.return_value = 2
        playlist_manager.remove_playlist(mock_parent)
        mock_parent.music_controller.stop_song.assert_called_once()
        mock_parent.ui_updater.clear_song_info.assert_called_once()
        playlist_manager.db_manager.delete_playlist.assert_called_once_with(
            "Test Playlist"
        )
        playlist_manager.list_widget.takeItem.assert_called_once_with(0)
        playlist_manager.list_widget.setCurrentRow.assert_called_once_with(0)
        assert mock_parent.current_playlist is None

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_remove_playlist_no_confirm(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test remove_playlist behavior when user does not confirm deletion.

        Verifies that when the user chooses not to confirm playlist deletion,
        no playlist operations are performed and the current playlist is unchanged.

        Args:
            mock_list_validator: Mocked list_validator module.
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.

        Returns:
            None
        """
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = True
        playlist_manager.list_widget.currentRow.return_value = 0
        mock_item = MagicMock()
        mock_item.text.return_value = "Test Playlist"
        playlist_manager.list_widget.item.return_value = mock_item
        mock_parent.current_playlist = "Test Playlist"
        playlist_manager.messanger.show_question.return_value = QMessageBox.No

        playlist_manager.remove_playlist(mock_parent)

        mock_parent.music_controller.stop_song.assert_not_called()
        playlist_manager.db_manager.delete_playlist.assert_not_called()
        assert mock_parent.current_playlist == "Test Playlist"

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_remove_playlist_database_error(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test remove_playlist handling of DatabaseError exceptions.

        Verifies that when a DatabaseError occurs during playlist deletion, the method
        properly catches the exception and displays an appropriate error message.

        Args:
            mock_list_validator: Mocked list_validator module.
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.

        Returns:
            None
        """
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = True
        playlist_manager.list_widget.currentRow.return_value = 0
        mock_item = MagicMock()
        mock_item.text.return_value = "Test Playlist"
        playlist_manager.list_widget.item.return_value = mock_item
        mock_parent.current_playlist = "Test Playlist"
        playlist_manager.messanger.show_question.return_value = QMessageBox.Yes
        playlist_manager.db_manager.delete_playlist.side_effect = DatabaseError(
            "DB error"
        )

        playlist_manager.remove_playlist(mock_parent)

        playlist_manager.messanger.show_critical.assert_called_once_with(
            mock_parent, msg.TTL_ERR, "Database error while removing playlist: DB error"
        )

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_remove_playlist_playlist_error(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test remove_playlist handling of PlaylistError exceptions.

        Verifies that when a PlaylistError occurs during playlist deletion, the method
        properly catches the exception and displays an appropriate error message.

        Args:
            mock_list_validator: Mocked list_validator module.
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.

        Returns:
            None
        """
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = True
        playlist_manager.list_widget.currentRow.return_value = 0
        mock_item = MagicMock()
        mock_item.text.return_value = "Test Playlist"
        playlist_manager.list_widget.item.return_value = mock_item
        mock_parent.current_playlist = "Test Playlist"
        playlist_manager.messanger.show_question.return_value = QMessageBox.Yes
        playlist_manager.db_manager.delete_playlist.side_effect = PlaylistError(
            "Playlist error"
        )
        playlist_manager.remove_playlist(mock_parent)
        playlist_manager.messanger.show_critical.assert_called_once_with(
            mock_parent, msg.TTL_ERR, "Playlist error: Playlist error"
        )

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_remove_playlist_item_none(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test remove_playlist behavior when item is unexpectedly None after selection.

        Verifies that when the selected playlist item is unexpectedly None, no playlist
        operations are performed to avoid exceptions.

        Args:
            mock_list_validator: Mocked list_validator module.
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.

        Returns:
            None
        """
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = True
        playlist_manager.list_widget.currentRow.return_value = 0
        playlist_manager.list_widget.item.return_value = None  # Item unexpectedly None
        playlist_manager.remove_playlist(mock_parent)
        mock_parent.music_controller.stop_song.assert_not_called()
        playlist_manager.db_manager.delete_playlist.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_remove_all_playlists(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test successful removal of all playlists.

        Verifies that when removing all playlists with confirmation, the method correctly
        stops any playing song, clears song info, deletes all playlists, clears the UI,
        and clears the current playlist reference.

        Args:
            mock_list_validator: Mocked list_validator module.
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.

        Returns:
            None
        """
        mock_list_validator.check_list_not_empty.return_value = True
        playlist_manager.messanger.show_question.return_value = QMessageBox.Yes
        mock_parent.current_playlist = "Test Playlist"
        playlist_manager.db_manager.get_playlists.return_value = [
            "Test Playlist",
            "Other Playlist",
        ]
        playlist_manager.remove_all_playlists(mock_parent)
        mock_parent.music_controller.stop_song.assert_called_once()
        mock_parent.ui_updater.clear_song_info.assert_called_once()
        assert mock_parent.current_playlist is None
        playlist_manager.db_manager.delete_playlist.assert_any_call("Test Playlist")
        playlist_manager.db_manager.delete_playlist.assert_any_call("Other Playlist")
        mock_parent.playlists_listWidget.clear.assert_called_once()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_remove_all_playlists_no_confirm(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test remove_all_playlists behavior when user does not confirm deletion.

        Verifies that when the user chooses not to confirm deletion of all playlists,
        no playlist operations are performed and the current playlist is unchanged.

        Args:
            mock_list_validator: Mocked list_validator module.
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.

        Returns:
            None
        """
        mock_list_validator.check_list_not_empty.return_value = True
        playlist_manager.messanger.show_question.return_value = QMessageBox.No
        mock_parent.current_playlist = "Test Playlist"
        playlist_manager.remove_all_playlists(mock_parent)
        mock_parent.music_controller.stop_song.assert_not_called()
        playlist_manager.db_manager.delete_playlist.assert_not_called()
        assert mock_parent.current_playlist == "Test Playlist"

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_remove_all_playlists_database_error(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test remove_all_playlists handling of DatabaseError exceptions.

        Verifies that when a DatabaseError occurs during deletion of all playlists,
        the method properly catches the exception and displays an appropriate error message.

        Args:
            mock_list_validator: Mocked list_validator module.
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.

        Returns:
            None
        """
        mock_list_validator.check_list_not_empty.return_value = True
        playlist_manager.messanger.show_question.return_value = QMessageBox.Yes
        mock_parent.current_playlist = "Test Playlist"
        playlist_manager.db_manager.get_playlists.return_value = ["Test Playlist"]
        playlist_manager.db_manager.delete_playlist.side_effect = DatabaseError(
            "DB error"
        )
        playlist_manager.remove_all_playlists(mock_parent)
        playlist_manager.messanger.show_critical.assert_called_once_with(
            mock_parent,
            msg.TTL_ERR,
            "Database error while removing playlists: DB error",
        )

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_remove_all_playlists_playlist_error(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test remove_all_playlists handling of PlaylistError exceptions.

        Verifies that when a PlaylistError occurs during deletion of all playlists,
        the method properly catches the exception and displays an appropriate error message.

        Args:
            mock_list_validator: Mocked list_validator module.
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.

        Returns:
            None
        """
        mock_list_validator.check_list_not_empty.return_value = True
        playlist_manager.messanger.show_question.return_value = QMessageBox.Yes
        mock_parent.current_playlist = "Test Playlist"
        playlist_manager.db_manager.get_playlists.return_value = ["Test Playlist"]
        playlist_manager.db_manager.delete_playlist.side_effect = PlaylistError(
            "Playlist error"
        )
        playlist_manager.remove_all_playlists(mock_parent)
        playlist_manager.messanger.show_critical.assert_called_once_with(
            mock_parent,
            msg.TTL_ERR,
            "Playlist error: Playlist error",
        )

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_remove_all_playlists_favourites(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test remove_all_playlists behavior when current playlist is 'favourites'.

        Verifies that when removing all playlists while the current playlist is 'favourites',
        the method preserves the 'favourites' playlist and only deletes other playlists.

        Args:
            mock_list_validator: Mocked list_validator module.
            playlist_manager: Fixture providing a PlaylistManager instance with mocked dependencies.
            mock_parent: Fixture providing a mock parent widget.

        Returns:
            None
        """
        mock_list_validator.check_list_not_empty.return_value = True
        playlist_manager.messanger.show_question.return_value = QMessageBox.Yes
        mock_parent.current_playlist = "favourites"
        playlist_manager.db_manager.get_playlists.return_value = ["Test Playlist"]
        playlist_manager.remove_all_playlists(mock_parent)
        mock_parent.music_controller.stop_song.assert_not_called()
        mock_parent.ui_updater.clear_song_info.assert_not_called()
        playlist_manager.db_manager.delete_playlist.assert_called_once_with(
            "Test Playlist"
        )
        mock_parent.playlists_listWidget.clear.assert_called_once()
        assert mock_parent.current_playlist == "favourites"

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_song_to_playlist_success(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test adding a song to a playlist with valid song and playlist selections.
        
        This test verifies that when a song is properly selected and a valid playlist
        is chosen, the song is successfully added to the playlist.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies db_manager.add_song_to_playlist is called with correct parameters
        """
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = True
        mock_item = MagicMock()
        mock_item.data.return_value = "song.mp3"
        mock_parent.loaded_songs_listWidget.currentItem.return_value = mock_item
        playlist_manager.ui_manager.select_playlist.return_value = (
            "Test Playlist",
            True,
        )
        playlist_manager.add_song_to_playlist(mock_parent)
        playlist_manager.db_manager.add_song_to_playlist.assert_called_once_with(
            "Test Playlist", "song.mp3"
        )

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_song_to_playlist_no_songs(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test adding a song to a playlist when the song list is empty.
        
        This test verifies that when attempting to add a song to a playlist
        with an empty song list, the playlist selection dialog is not displayed.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies ui_manager.select_playlist is not called when song list is empty
        """
        mock_list_validator.check_list_not_empty.return_value = False
        playlist_manager.add_song_to_playlist(mock_parent)
        playlist_manager.ui_manager.select_playlist.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_song_to_playlist_no_selection(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test adding a song to a playlist when no song is selected.
        
        This test verifies that when attempting to add a song to a playlist
        with no song selected, the playlist selection dialog is not displayed.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies ui_manager.select_playlist is not called when no song is selected
        """
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = False
        playlist_manager.add_song_to_playlist(mock_parent)
        playlist_manager.ui_manager.select_playlist.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_song_to_playlist_cancel(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test adding a song to a playlist when the user cancels the playlist selection dialog.
        
        This test verifies that when the user cancels the playlist selection dialog,
        no database operation is performed.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies db_manager.add_song_to_playlist is not called when playlist selection is canceled
        """
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = True
        mock_item = MagicMock()
        mock_item.data.return_value = "song.mp3"
        mock_parent.loaded_songs_listWidget.currentItem.return_value = mock_item
        playlist_manager.ui_manager.select_playlist.return_value = (
            "Test Playlist",
            False,
        )
        playlist_manager.add_song_to_playlist(mock_parent)
        playlist_manager.db_manager.add_song_to_playlist.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_song_to_playlist_no_selection_made(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test adding a song to a playlist when no playlist is actually selected.
        
        This test verifies that when the default placeholder "--Click to Select--" remains selected,
        an information message is displayed and no database operation is performed.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies messanger.show_info is called with appropriate message
            - Verifies db_manager.add_song_to_playlist is not called
        """
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = True
        mock_item = MagicMock()
        mock_item.data.return_value = "song.mp3"
        mock_parent.loaded_songs_listWidget.currentItem.return_value = mock_item
        playlist_manager.ui_manager.select_playlist.return_value = (
            "--Click to Select--",
            True,
        )
        playlist_manager.add_song_to_playlist(mock_parent)
        playlist_manager.messanger.show_info.assert_called_once_with(
            mock_parent, msg.TTL_ADD_TO_LST, msg.MSG_NO_LST_SEL
        )
        playlist_manager.db_manager.add_song_to_playlist.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_song_to_playlist_item_none(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test adding a song to a playlist when currentItem returns None.
        
        This test verifies that when currentItem unexpectedly returns None despite
        validation passing, an information message is displayed and no database operation is performed.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies messanger.show_info is called with appropriate message
            - Verifies db_manager.add_song_to_playlist is not called
        """
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = True
        mock_parent.loaded_songs_listWidget.currentItem.return_value = None
        playlist_manager.add_song_to_playlist(mock_parent)
        playlist_manager.messanger.show_info.assert_called_once_with(
            mock_parent, msg.TTL_ATT, msg.MSG_NO_SONG_SEL
        )
        playlist_manager.db_manager.add_song_to_playlist.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_song_to_playlist_integrity_error(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test adding a song to a playlist when an IntegrityError occurs (duplicate song).
        
        This test verifies that when attempting to add a song that's already in the playlist,
        an IntegrityError is caught and a warning message is displayed to the user.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies messanger.show_warning is called with appropriate message
        """
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = True
        mock_item = MagicMock()
        mock_item.data.return_value = "song.mp3"
        mock_parent.loaded_songs_listWidget.currentItem.return_value = mock_item
        playlist_manager.ui_manager.select_playlist.return_value = (
            "Test Playlist",
            True,
        )
        playlist_manager.db_manager.add_song_to_playlist.side_effect = IntegrityError(
            "Duplicate"
        )
        playlist_manager.add_song_to_playlist(mock_parent)
        playlist_manager.messanger.show_warning.assert_called_once_with(
            mock_parent, msg.TTL_WRN, f"{msg.MSG_SONG_EXIST} Test Playlist."
        )

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_song_to_playlist_database_error(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test adding a song to a playlist when a DatabaseError occurs.
        
        This test verifies that when a general database error occurs during song addition,
        the error is caught and a critical message is displayed to the user.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies messanger.show_critical is called with appropriate message
        """
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = True
        mock_item = MagicMock()
        mock_item.data.return_value = "song.mp3"
        mock_parent.loaded_songs_listWidget.currentItem.return_value = mock_item
        playlist_manager.ui_manager.select_playlist.return_value = (
            "Test Playlist",
            True,
        )
        playlist_manager.db_manager.add_song_to_playlist.side_effect = DatabaseError(
            "DB error"
        )
        playlist_manager.add_song_to_playlist(mock_parent)
        playlist_manager.messanger.show_critical.assert_called_once_with(
            mock_parent, msg.TTL_ERR, "Database error while adding song: DB error"
        )

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_song_to_playlist_playlist_error(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test adding a song to a playlist when a PlaylistError occurs.
        
        This test verifies that when a playlist-specific error occurs during song addition,
        the error is caught and a critical message is displayed to the user.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies messanger.show_critical is called with appropriate message
        """
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = True
        mock_item = MagicMock()
        mock_item.data.return_value = "song.mp3"
        mock_parent.loaded_songs_listWidget.currentItem.return_value = mock_item
        playlist_manager.ui_manager.select_playlist.return_value = (
            "Test Playlist",
            True,
        )
        playlist_manager.db_manager.add_song_to_playlist.side_effect = PlaylistError(
            "Playlist error"
        )
        playlist_manager.add_song_to_playlist(mock_parent)
        playlist_manager.messanger.show_critical.assert_called_once_with(
            mock_parent, msg.TTL_ERR, "Playlist error: Playlist error"
        )

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_all_to_playlist(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test adding all songs from the loaded songs list to a playlist.
        
        This test verifies that when adding all songs to a playlist, each valid song
        is processed correctly and a summary message is displayed with the count of added songs.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies db_manager.add_song_to_playlist is called for each valid song
            - Verifies messanger.show_info is called with song count summary
        """
        mock_list_validator.check_list_not_empty.return_value = True
        playlist_manager.ui_manager.select_playlist.return_value = (
            "Test Playlist",
            True,
        )
        mock_parent.loaded_songs_listWidget.count.return_value = 3
        mock_items = [MagicMock() for _ in range(3)]
        mock_items[0].data.return_value = "song1.mp3"
        mock_items[1].data.return_value = "song2.mp3"
        mock_items[2].data.return_value = None
        mock_parent.loaded_songs_listWidget.item.side_effect = mock_items
        playlist_manager.add_all_to_playlist(mock_parent)
        playlist_manager.db_manager.add_song_to_playlist.assert_any_call(
            "Test Playlist", "song1.mp3"
        )
        playlist_manager.db_manager.add_song_to_playlist.assert_any_call(
            "Test Playlist", "song2.mp3"
        )
        playlist_manager.messanger.show_info.assert_called_once_with(
            mock_parent, msg.TTL_OK, f"2 {msg.CTX_ADD_ALL_TO_LST}"
        )

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_all_to_playlist_no_songs(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test adding all songs to a playlist when the song list is empty.
        
        This test verifies that when attempting to add all songs to a playlist
        with an empty song list, the playlist selection dialog is not displayed.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies ui_manager.select_playlist is not called when song list is empty
        """
        mock_list_validator.check_list_not_empty.return_value = False
        playlist_manager.add_all_to_playlist(mock_parent)
        playlist_manager.ui_manager.select_playlist.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_all_to_playlist_cancel(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test adding all songs to a playlist when the user cancels the playlist selection dialog.
        
        This test verifies that when the user cancels the playlist selection dialog,
        no database operations are performed.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies db_manager.add_song_to_playlist is not called when playlist selection is canceled
        """
        mock_list_validator.check_list_not_empty.return_value = True
        playlist_manager.ui_manager.select_playlist.return_value = (
            "Test Playlist",
            False,
        )
        playlist_manager.add_all_to_playlist(mock_parent)
        playlist_manager.db_manager.add_song_to_playlist.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_all_to_playlist_no_selection_made(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test adding all songs to a playlist when no playlist is actually selected.
        
        This test verifies that when the default placeholder "--Click to Select--" remains selected,
        an information message is displayed and no database operations are performed.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies messanger.show_info is called with appropriate message
            - Verifies db_manager.add_song_to_playlist is not called
        """
        mock_list_validator.check_list_not_empty.return_value = True
        playlist_manager.ui_manager.select_playlist.return_value = (
            "--Click to Select--",
            True,
        )
        playlist_manager.add_all_to_playlist(mock_parent)
        playlist_manager.messanger.show_info.assert_called_once_with(
            mock_parent, msg.TTL_ADD_TO_LST, msg.MSG_NO_LST_SEL
        )
        playlist_manager.db_manager.add_song_to_playlist.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_all_to_playlist_database_error(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test adding all songs to a playlist when a DatabaseError occurs.
        
        This test verifies that when a general database error occurs during bulk song addition,
        the error is caught and a critical message is displayed to the user.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies messanger.show_critical is called with appropriate message
        """
        mock_list_validator.check_list_not_empty.return_value = True
        playlist_manager.ui_manager.select_playlist.return_value = (
            "Test Playlist",
            True,
        )
        mock_parent.loaded_songs_listWidget.count.return_value = 2
        mock_items = [MagicMock(), MagicMock()]
        mock_items[0].data.return_value = "song1.mp3"
        mock_items[1].data.return_value = "song2.mp3"
        mock_parent.loaded_songs_listWidget.item.side_effect = mock_items
        playlist_manager.db_manager.add_song_to_playlist.side_effect = DatabaseError(
            "DB error"
        )
        playlist_manager.add_all_to_playlist(mock_parent)
        playlist_manager.messanger.show_critical.assert_called_once_with(
            mock_parent, msg.TTL_ERR, "Failed to add song to playlist: DB error"
        )

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_all_to_playlist_value_error(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test adding all songs to a playlist when a ValueError occurs.
        
        This test verifies that when a ValueError occurs during data processing,
        the error is caught and a critical message is displayed to the user.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies messanger.show_critical is called with appropriate message
        """
        mock_list_validator.check_list_not_empty.return_value = True
        playlist_manager.ui_manager.select_playlist.side_effect = ValueError(
            "Invalid data"
        )
        mock_parent.loaded_songs_listWidget.count.return_value = 2
        mock_items = [MagicMock(), MagicMock()]
        mock_items[0].data.return_value = "song1.mp3"
        mock_items[1].data.return_value = "song2.mp3"
        mock_parent.loaded_songs_listWidget.item.side_effect = mock_items
        playlist_manager.add_all_to_playlist(mock_parent)
        playlist_manager.messanger.show_critical.assert_called_once_with(
            mock_parent, msg.TTL_ERR, "Invalid data format: Invalid data"
        )

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_all_to_playlist_playlist_error(self, mock_list_validator, playlist_manager, mock_parent):
        """
        Test adding all songs to a playlist when a PlaylistError occurs.
        
        This test verifies that when a playlist-specific error occurs during bulk song addition,
        the error is caught and a critical message is displayed to the user.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies messanger.show_critical is called with appropriate message
        """
        mock_list_validator.check_list_not_empty.return_value = True
        playlist_manager.ui_manager.select_playlist.return_value = ("Test Playlist", True)
        mock_parent.loaded_songs_listWidget.count.return_value = 2
        mock_items = [MagicMock(), MagicMock()]
        mock_items[0].data.return_value = "song1.mp3"
        mock_items[1].data.return_value = "song2.mp3"
        mock_parent.loaded_songs_listWidget.item.side_effect = mock_items
        playlist_manager.db_manager.add_song_to_playlist.side_effect = PlaylistError("Playlist error")
        playlist_manager.add_all_to_playlist(mock_parent)
        playlist_manager.messanger.show_critical.assert_called_once_with(
            mock_parent, msg.TTL_ERR, "Playlist error"
        )

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_load_playlist_into_widget_item_none(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test loading a playlist into widget when the selected item is None.
        
        This test verifies that when attempting to load a playlist but the selected item
        is unexpectedly None, no loading operation is performed.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies ui_manager.load_playlist is not called
            - Verifies parent.switch_to_songs_tab is not called
        """
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = True
        playlist_manager.list_widget.currentRow.return_value = 0
        playlist_manager.list_widget.item.return_value = None
        playlist_manager.load_playlist_into_widget(mock_parent)
        playlist_manager.ui_manager.load_playlist.assert_not_called()
        mock_parent.switch_to_songs_tab.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_remove_playlist_empty_list(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test removing a playlist when the playlist list is empty.
        
        This test verifies that when attempting to remove a playlist with an empty playlist list,
        the validation fails and no removal operation is performed.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies check_list_not_empty is called with appropriate message
            - Verifies music_controller.stop_song is not called
            - Verifies db_manager.delete_playlist is not called
        """
        mock_list_validator.check_list_not_empty.return_value = False
        playlist_manager.remove_playlist(mock_parent)
        mock_list_validator.check_list_not_empty.assert_called_once_with(
            playlist_manager.list_widget, "There are no playlists to be deleted"
        )
        mock_parent.music_controller.stop_song.assert_not_called()
        playlist_manager.db_manager.delete_playlist.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_remove_playlist_no_selection(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test removing a playlist when no playlist is selected.
        
        This test verifies that when attempting to remove a playlist with no selection,
        the validation fails and no removal operation is performed.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies check_item_selected is called with appropriate message
            - Verifies music_controller.stop_song is not called
            - Verifies db_manager.delete_playlist is not called
        """
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = False
        playlist_manager.remove_playlist(mock_parent)
        mock_list_validator.check_item_selected.assert_called_once_with(
            playlist_manager.list_widget, mock_parent, message=msg.MSG_NO_LST_SEL
        )
        mock_parent.music_controller.stop_song.assert_not_called()
        playlist_manager.db_manager.delete_playlist.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_remove_all_playlists_empty_list(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test removing all playlists when the playlist list is empty.
        
        This test verifies that when attempting to remove all playlists with an empty playlist list,
        the validation fails and no removal operations are performed.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies check_list_not_empty is called with appropriate message
            - Verifies music_controller.stop_song is not called
            - Verifies db_manager.delete_playlist is not called
        """
        mock_list_validator.check_list_not_empty.return_value = False
        playlist_manager.remove_all_playlists(mock_parent)
        mock_list_validator.check_list_not_empty.assert_called_once_with(
            mock_parent.playlists_listWidget, "There are no playlists to be deleted"
        )
        mock_parent.music_controller.stop_song.assert_not_called()
        playlist_manager.db_manager.delete_playlist.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_all_to_playlist_integrity_error(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test adding all songs to a playlist when an IntegrityError occurs for some songs.
        
        This test verifies that when adding multiple songs to a playlist and some cause
        IntegrityErrors (duplicate songs), the operation continues for the remaining songs
        and a summary message with the successful count is displayed.
        
        Args:
            mock_list_validator: Mocked list_validator module for validation control
            playlist_manager: The PlaylistManager instance under test
            mock_parent: Mock of the parent window/widget containing required UI elements
        
        Returns:
            None
        
        Side effects:
            - Verifies db_manager.add_song_to_playlist is called for each song
            - Verifies messanger.show_info is called with successful song count
            - Verifies messanger.show_critical is not called (integrity errors are expected)
        """
        mock_list_validator.check_list_not_empty.return_value = True
        playlist_manager.ui_manager.select_playlist.return_value = (
            "Test Playlist",
            True,
        )
        mock_parent.loaded_songs_listWidget.count.return_value = 2
        mock_items = [MagicMock(), MagicMock()]
        mock_items[0].data.return_value = "song1.mp3"
        mock_items[1].data.return_value = "song2.mp3"
        mock_parent.loaded_songs_listWidget.item.side_effect = mock_items
        playlist_manager.db_manager.add_song_to_playlist.side_effect = [
            None,
            IntegrityError("Duplicate"),
        ]
        playlist_manager.add_all_to_playlist(mock_parent)
        playlist_manager.db_manager.add_song_to_playlist.assert_any_call(
            "Test Playlist", "song1.mp3"
        )
        playlist_manager.db_manager.add_song_to_playlist.assert_any_call(
            "Test Playlist", "song2.mp3"
        )
        playlist_manager.messanger.show_info.assert_called_once_with(
            mock_parent, msg.TTL_OK, f"1 {msg.CTX_ADD_ALL_TO_LST}"
        )
        playlist_manager.messanger.show_critical.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_all_to_playlist_outer_database_error(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """
        Test that add_all_to_playlist properly handles a DatabaseError occurring outside the loop.

        This test verifies that when a DatabaseError is raised during the playlist selection process,
        the error is caught, the appropriate error message is displayed, and no attempts are made
        to add songs to the playlist.

        Args:
            mock_list_validator: Mock object for the list_validator module, used to control
                                 the behavior of check_list_not_empty method.
            playlist_manager: Fixture providing the PlaylistManager instance under test.
            mock_parent: Mock object representing the parent UI element.

        Returns:
            None

        Side effects:
            - Verifies that show_critical is called with the appropriate error message
            - Confirms that add_song_to_playlist is not called when the error occurs
        """
        mock_list_validator.check_list_not_empty.return_value = True
        playlist_manager.ui_manager.select_playlist.side_effect = DatabaseError(
            "DB error"
        )
        playlist_manager.add_all_to_playlist(mock_parent)

        playlist_manager.messanger.show_critical.assert_called_once_with(
            mock_parent, msg.TTL_ERR, "Database error while adding songs: DB error"
        )
        playlist_manager.db_manager.add_song_to_playlist.assert_not_called()

from sqlite3 import IntegrityError, DatabaseError
from unittest.mock import MagicMock, patch
import pytest
from PyQt5.QtWidgets import QListWidget, QMessageBox

from interfaces.playlists.playlist_manager import PlaylistManager, PlaylistError
from utils import messages as msg


class TestPlaylistManager:
    @pytest.fixture
    def playlist_manager(self):
        """Fixture to create a PlaylistManager instance with mocked dependencies."""
        mock_db_manager = MagicMock()
        mock_playlist_widget = MagicMock(spec=QListWidget)
        playlist_manager = PlaylistManager(mock_db_manager, mock_playlist_widget)

        # Мокаем методы ui_manager и db_manager
        playlist_manager.ui_manager.load_playlists = MagicMock()
        playlist_manager.ui_manager.load_playlist = MagicMock()
        playlist_manager.ui_manager.select_playlist = MagicMock()
        playlist_manager.db_manager.get_playlists = MagicMock()
        playlist_manager.db_manager.create_playlist = MagicMock()
        playlist_manager.db_manager.delete_playlist = MagicMock()
        playlist_manager.db_manager.add_song_to_playlist = MagicMock()

        # Мокаем методы messanger
        playlist_manager.messanger.show_info = MagicMock()
        playlist_manager.messanger.show_warning = MagicMock()
        playlist_manager.messanger.show_critical = MagicMock()
        playlist_manager.messanger.show_question = MagicMock()

        return playlist_manager

    @pytest.fixture
    def mock_parent(self):
        """Fixture to create a mock parent widget."""
        parent = MagicMock()
        parent.loaded_songs_listWidget = MagicMock(spec=QListWidget)
        parent.playlists_listWidget = MagicMock(spec=QListWidget)
        parent.music_controller = MagicMock()
        parent.ui_updater = MagicMock()
        parent.switch_to_songs_tab = MagicMock()
        return parent

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_load_playlists_into_widget(self, mock_list_validator, playlist_manager):
        """Test load_playlists_into_widget calls ui_manager.load_playlists."""
        playlist_manager.load_playlists_into_widget()
        playlist_manager.ui_manager.load_playlists.assert_called_once()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_load_playlist_into_widget_empty_list(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """Test load_playlist_into_widget with empty list."""
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
        """Test load_playlist_into_widget with no selection."""
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
        """Test load_playlist_into_widget with valid selection."""
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
        """Test load_playlist_into_widget with DatabaseError."""
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
        """Test load_playlist_into_widget with PlaylistError."""
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
        """Test create_playlist with a new playlist name."""
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
        """Test create_playlist with cancel or empty name."""
        playlist_manager.db_manager.get_playlists.return_value = ["Existing Playlist"]
        with patch(
            "interfaces.playlists.playlist_manager.QInputDialog.getText",
            return_value=("", False),
        ):
            result = playlist_manager.create_playlist(mock_parent)

        playlist_manager.db_manager.create_playlist.assert_not_called()
        assert result is None

    def test_create_playlist_value_error(self, playlist_manager, mock_parent):
        """Test create_playlist with ValueError."""
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
        """Test create_playlist with DatabaseError."""
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
        """Test create_playlist with no replacement."""
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
        """Test create_playlist replacing an existing playlist."""
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
        """Test remove_playlist with valid selection."""
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
        """Test remove_playlist with no confirmation."""
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
        """Test remove_playlist with DatabaseError."""
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
        """Test remove_playlist with PlaylistError."""
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
        """Test remove_playlist when item is None after selection."""
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
        """Test remove_all_playlists with confirmation."""
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
        """Test remove_all_playlists with no confirmation."""
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
        """Test remove_all_playlists with DatabaseError."""
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
        """Test remove_all_playlists with PlaylistError."""
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
        """Test remove_all_playlists when current playlist is 'favourites'."""
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
        """Test add_song_to_playlist with valid song and playlist."""
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
        """Test add_song_to_playlist with empty song list."""
        mock_list_validator.check_list_not_empty.return_value = False
        playlist_manager.add_song_to_playlist(mock_parent)
        playlist_manager.ui_manager.select_playlist.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_song_to_playlist_no_selection(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """Test add_song_to_playlist with no song selected."""
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = False
        playlist_manager.add_song_to_playlist(mock_parent)
        playlist_manager.ui_manager.select_playlist.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_song_to_playlist_cancel(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """Test add_song_to_playlist with cancel."""
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
        """Test add_song_to_playlist with '--Click to Select--'."""
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
        """Test add_song_to_playlist when currentItem returns None."""
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
        """Test add_song_to_playlist with IntegrityError."""
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
        """Test add_song_to_playlist with DatabaseError."""
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
        """Test add_song_to_playlist with PlaylistError."""
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
        """Test add_all_to_playlist with multiple songs."""
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
        """Test add_all_to_playlist with empty list."""
        mock_list_validator.check_list_not_empty.return_value = False
        playlist_manager.add_all_to_playlist(mock_parent)
        playlist_manager.ui_manager.select_playlist.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_all_to_playlist_cancel(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """Test add_all_to_playlist with cancel."""
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
        """Test add_all_to_playlist with '--Click to Select--'."""
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
        """Test add_all_to_playlist with DatabaseError."""
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
        """Test add_all_to_playlist with ValueError."""
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
        """Test add_all_to_playlist with PlaylistError."""
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
            mock_parent, msg.TTL_ERR, "Playlist error"  # Исправленное ожидаемое сообщение
        )

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_load_playlist_into_widget_item_none(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """Test load_playlist_into_widget when item is None."""
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = True
        playlist_manager.list_widget.currentRow.return_value = 0
        playlist_manager.list_widget.item.return_value = None  # Условие 3

        playlist_manager.load_playlist_into_widget(mock_parent)

        playlist_manager.ui_manager.load_playlist.assert_not_called()
        mock_parent.switch_to_songs_tab.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_remove_playlist_empty_list(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """Test remove_playlist with empty list."""
        mock_list_validator.check_list_not_empty.return_value = False  # Условие 1

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
        """Test remove_playlist with no selection."""
        mock_list_validator.check_list_not_empty.return_value = True
        mock_list_validator.check_item_selected.return_value = False  # Условие 2

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
        """Test remove_all_playlists with empty list."""
        mock_list_validator.check_list_not_empty.return_value = False  # Условие 1

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
        """Test add_all_to_playlist with IntegrityError for duplicate songs."""
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
        # Первая песня добавляется успешно, вторая вызывает IntegrityError
        playlist_manager.db_manager.add_song_to_playlist.side_effect = [
            None,  # Успешно для song1.mp3
            IntegrityError("Duplicate"),  # Ошибка для song2.mp3
        ]

        playlist_manager.add_all_to_playlist(mock_parent)

        # Проверяем, что добавлена только первая песня
        playlist_manager.db_manager.add_song_to_playlist.assert_any_call(
            "Test Playlist", "song1.mp3"
        )
        playlist_manager.db_manager.add_song_to_playlist.assert_any_call(
            "Test Playlist", "song2.mp3"
        )
        playlist_manager.messanger.show_info.assert_called_once_with(
            mock_parent, msg.TTL_OK, f"1 {msg.CTX_ADD_ALL_TO_LST}"
        )
        # Убеждаемся, что IntegrityError не вызвало критическую ошибку
        playlist_manager.messanger.show_critical.assert_not_called()

    @patch("interfaces.playlists.playlist_manager.list_validator")
    def test_add_all_to_playlist_outer_database_error(
        self, mock_list_validator, playlist_manager, mock_parent
    ):
        """Test add_all_to_playlist with DatabaseError outside the loop."""
        mock_list_validator.check_list_not_empty.return_value = True
        # Ошибка возникает на этапе выбора плейлиста
        playlist_manager.ui_manager.select_playlist.side_effect = DatabaseError(
            "DB error"
        )

        playlist_manager.add_all_to_playlist(mock_parent)

        playlist_manager.messanger.show_critical.assert_called_once_with(
            mock_parent, msg.TTL_ERR, "Database error while adding songs: DB error"
        )
        playlist_manager.db_manager.add_song_to_playlist.assert_not_called()

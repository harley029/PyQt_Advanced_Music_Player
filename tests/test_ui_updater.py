# pylint: disable=redefined-outer-name
import os
from unittest.mock import MagicMock, patch
import pytest

from PyQt5.QtMultimedia import QMediaPlayer

from utils.message_manager import MessageManager
from controllers.ui_updater import UIUpdater, SongInfoLabels, UIElements


# Патчим QTimer, который используется в модуле controllers.ui_updater
@pytest.fixture
def mock_timer():
    """Fixture to mock QTimer."""
    with patch("controllers.ui_updater.QTimer", autospec=True) as mock_timer_class:
        mock_timer_instance = MagicMock()
        mock_timer_class.return_value = mock_timer_instance
        yield mock_timer_instance


# Патчим File, импортированный в controllers.ui_updater (из mutagen)
@pytest.fixture
def mock_file():
    """Fixture to mock mutagen.File."""
    with patch("controllers.ui_updater.File") as mock_file:
        yield mock_file


# Патчим MessageManager, который импортируется в controllers.ui_updater
@pytest.fixture
def mock_message_manager():
    """Fixture to mock MessageManager."""
    mock_mgr = MagicMock(spec=MessageManager)
    with patch("controllers.ui_updater.MessageManager", return_value=mock_mgr):
        yield mock_mgr


@pytest.fixture
def ui_elements():
    """Create mocked UI elements for testing."""
    mock_slider = MagicMock()
    mock_time_label = MagicMock()
    mock_title_label = MagicMock()
    mock_artist_label = MagicMock()
    mock_album_label = MagicMock()
    mock_duration_label = MagicMock()

    song_info = SongInfoLabels(
        mock_title_label, mock_artist_label, mock_album_label, mock_duration_label
    )

    return UIElements(
        slider=mock_slider, time_label=mock_time_label, song_info=song_info
    )


@pytest.fixture
def mock_music_controller():
    """Create a mock music controller."""
    mock_controller = MagicMock()
    mock_player = MagicMock(spec=QMediaPlayer)
    mock_controller.media_player.return_value = mock_player
    mock_controller.is_stopped = False
    return mock_controller


@pytest.fixture
def ui_updater(mock_music_controller, ui_elements, mock_timer, mock_message_manager):
    """Create UIUpdater instance with mocked dependencies."""
    parent = MagicMock()
    updater = UIUpdater(mock_music_controller, ui_elements, parent)
    return updater


class TestUIUpdater:
    """Tests for the UIUpdater class."""

    def test_initialization(self, ui_updater, mock_timer):
        """Test that UIUpdater initializes correctly."""
        # Проверяем начальное состояние
        assert ui_updater.is_slider_moving is False
        # Проверяем, что таймер настроен правильно:
        mock_timer.setInterval.assert_called_with(1000)
        mock_timer.timeout.connect.assert_called()
        mock_timer.start.assert_called()

    def test_update_slider_when_stopped(self, ui_updater):
        """Test that slider doesn't update when player is stopped."""
        ui_updater.music_controller.is_stopped = True
        ui_updater.update_slider()
        assert not ui_updater.slider.setValue.called

    def test_update_slider_when_slider_moving(self, ui_updater):
        """Test that slider doesn't update when it's being moved by user."""
        ui_updater.is_slider_moving = True
        ui_updater.update_slider()
        assert not ui_updater.slider.setValue.called

    def test_update_slider_playing(self, ui_updater):
        """Test slider updates correctly when media is playing."""
        player = ui_updater.music_controller.media_player()
        player.state.return_value = QMediaPlayer.PlayingState
        player.duration.return_value = 180000  # 3 minutes in ms
        player.position.return_value = 60000  # 1 minute in ms

        ui_updater.update_slider()

        ui_updater.slider.setMinimum.assert_called_once_with(0)
        ui_updater.slider.setMaximum.assert_called_once_with(180000)
        ui_updater.slider.setValue.assert_called_once_with(60000)
        ui_updater.time_label.setText.assert_called_once_with("00:01:00 / 00:03:00")

    def test_update_current_song_info_success(self, ui_updater, mock_file):
        """Test updating song info with valid metadata."""
        song_path = "test_song.mp3"

        # Mock audio file with tags
        mock_audio = MagicMock()
        tags_dict = {
        "TIT2": "Test Title",
        "TPE1": "Test Artist",
        "TALB": "Test Album",
    }
        mock_audio.tags.get.side_effect = tags_dict.get  # Use dict.get directly
        mock_audio.info.length = 185  # 3:05 in seconds

        mock_file.return_value = mock_audio

        ui_updater.update_current_song_info(song_path)

        ui_updater.song_info.title.setText.assert_called_once_with("Test Title")
        ui_updater.song_info.artist.setText.assert_called_once_with("Test Artist")
        ui_updater.song_info.album.setText.assert_called_once_with("Test Album")
        ui_updater.song_info.duration.setText.assert_called_once_with("0:03:05")

    def test_update_current_song_info_no_tags(self, ui_updater, mock_file):
        """Test updating song info with no metadata tags."""
        song_path = "test_song.mp3"
        filename = os.path.basename(song_path)

        # Mock audio file without tags
        mock_audio = MagicMock()
        mock_audio.tags = None
        mock_audio.info.length = 240  # 4 minutes in seconds

        mock_file.return_value = mock_audio

        ui_updater.update_current_song_info(song_path)

        ui_updater.song_info.title.setText.assert_called_once_with(filename)
        ui_updater.song_info.artist.setText.assert_called_once_with("Unknown Artist")
        ui_updater.song_info.album.setText.assert_called_once_with("Unknown Album")
        ui_updater.song_info.duration.setText.assert_called_once_with("0:04:00")

    def test_update_current_song_info_error(
        self, ui_updater, mock_file, mock_message_manager
    ):
        """Test handling of errors when updating song info."""
        song_path = "test_song.mp3"

        # Simulate an error when reading file
        mock_file.side_effect = OSError("Test error")

        ui_updater.update_current_song_info(song_path)

        # Check error message was shown
        mock_message_manager.show_critical.assert_called_once()

        # Check default values were used
        ui_updater.song_info.title.setText.assert_called_once_with(
            os.path.basename(song_path)
        )
        ui_updater.song_info.artist.setText.assert_called_once_with("Unknown Artist")
        ui_updater.song_info.album.setText.assert_called_once_with("Unknown Album")
        ui_updater.song_info.duration.setText.assert_called_once_with("0:00:00")

    def test_clear_song_info(self, ui_updater):
        """Test clearing song information."""
        ui_updater.clear_song_info()

        ui_updater.song_info.title.setText.assert_called_once_with("")
        ui_updater.song_info.artist.setText.assert_called_once_with("")
        ui_updater.song_info.album.setText.assert_called_once_with("")
        ui_updater.song_info.duration.setText.assert_called_once_with("")
        ui_updater.time_label.setText.assert_called_once_with("00:00:00 / 00:00:00")
        ui_updater.slider.setValue.assert_called_once_with(0)


class TestSongInfoLabels:
    """Tests for the SongInfoLabels class."""

    def test_initialization(self):
        """Test that SongInfoLabels initializes correctly."""
        title_label = MagicMock()
        artist_label = MagicMock()
        album_label = MagicMock()
        duration_label = MagicMock()

        labels = SongInfoLabels(title_label, artist_label, album_label, duration_label)

        assert labels.title == title_label
        assert labels.artist == artist_label
        assert labels.album == album_label
        assert labels.duration == duration_label


class TestMessageManager:
    """Tests for the MessageManager class."""

    @patch("utils.message_manager.QMessageBox")
    def test_show_info(self, mock_qmessagebox):
        """Test showing an info message."""
        parent = MagicMock()
        title = "Info Title"
        message = "Info Message"

        mgr = MessageManager()
        mgr.show_info(parent, title, message)

        mock_qmessagebox.information.assert_called_once_with(parent, title, message)

    @patch("utils.message_manager.QMessageBox")
    def test_show_warning(self, mock_qmessagebox):
        """Test showing a warning message."""
        parent = MagicMock()
        title = "Warning Title"
        message = "Warning Message"

        mgr = MessageManager()
        mgr.show_warning(parent, title, message)

        mock_qmessagebox.warning.assert_called_once_with(parent, title, message)

    @patch("utils.message_manager.QMessageBox")
    def test_show_critical(self, mock_qmessagebox):
        """Test showing a critical message without exception."""
        parent = MagicMock()
        title = "Error Title"
        message = "Error Message"

        mgr = MessageManager()
        mgr.show_critical(parent, title, message)

        mock_qmessagebox.critical.assert_called_once_with(parent, title, message)

    @patch("utils.message_manager.QMessageBox")
    def test_show_critical_with_exception(self, mock_qmessagebox):
        """Test showing a critical message with exception details."""
        parent = MagicMock()
        title = "Error Title"
        message = "Error Message"
        exception = Exception("Test exception")

        mgr = MessageManager()
        mgr.show_critical(parent, title, message, exception)

        expected_message = "Error Message\nError details: Test exception"
        mock_qmessagebox.critical.assert_called_once_with(
            parent, title, expected_message
        )

    @patch("utils.message_manager.QMessageBox")
    def test_show_question(self, mock_qmessagebox):
        """Test showing a question message."""
        parent = MagicMock()
        title = "Question Title"
        message = "Question Message"
        mock_qmessagebox.Yes = 16384  # Actual PyQt value
        mock_qmessagebox.No = 65536  # Actual PyQt value

        mgr = MessageManager()
        result = mgr.show_question(parent, title, message)

        mock_qmessagebox.question.assert_called_once_with(
            parent,
            title,
            message,
            mock_qmessagebox.Yes | mock_qmessagebox.No,
            mock_qmessagebox.No,
        )
        assert result == mock_qmessagebox.question.return_value

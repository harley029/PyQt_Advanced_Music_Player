# pylint: disable=redefined-outer-name
import os
from unittest.mock import MagicMock, patch
import pytest

from PyQt5.QtMultimedia import QMediaPlayer

from utils.message_manager import MessageManager
from controllers.ui_updater import UIUpdater, SongInfoLabels, UIElements


@pytest.fixture
def mock_timer():
    """
    Create a mock QTimer instance for testing.

    This fixture mocks the QTimer class from PyQt5 and returns
    a MagicMock instance that can be used to verify timer interactions.

    Returns:
        MagicMock: A mock instance of QTimer.
    """
    with patch("controllers.ui_updater.QTimer", autospec=True) as mock_timer_class:
        mock_timer_instance = MagicMock()
        mock_timer_class.return_value = mock_timer_instance
        yield mock_timer_instance


@pytest.fixture
def mock_file():
    """
    Create a mock for the mutagen.File class.

    This fixture provides a mock for the File class from the mutagen library,
    which is used for reading audio file metadata.

    Returns:
        MagicMock: A mock of the mutagen.File class.
    """
    with patch("controllers.ui_updater.File") as mock_file:
        yield mock_file


@pytest.fixture
def mock_message_manager():
    """
    Create a mock MessageManager instance.

    This fixture creates a mock of the MessageManager class and patches the
    import in the ui_updater module to return this mock.

    Returns:
        MagicMock: A mock instance of MessageManager with its interface
                  defined by the MessageManager spec.
    """
    mock_mgr = MagicMock(spec=MessageManager)
    with patch("controllers.ui_updater.MessageManager", return_value=mock_mgr):
        yield mock_mgr


@pytest.fixture
def ui_elements():
    """
    Create mocked UI elements for testing the UIUpdater.

    This fixture creates mock objects for all UI elements required by the UIUpdater,
    including slider, time label, and song info labels.

    Returns:
        UIElements: An instance of UIElements containing all necessary mock UI components.
    """
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
    """
    Create a mock music controller for testing.

    This fixture creates a mock of the music controller with necessary
    attributes and methods required for UIUpdater tests, including
    a mock media player.

    Returns:
        MagicMock: A configured mock music controller with a media_player method
                  that returns a mock QMediaPlayer.
    """
    mock_controller = MagicMock()
    mock_player = MagicMock(spec=QMediaPlayer)
    mock_controller.media_player.return_value = mock_player
    mock_controller.is_stopped = False
    return mock_controller


@pytest.fixture
def ui_updater(mock_music_controller, ui_elements, mock_timer, mock_message_manager):
    """
    Create a UIUpdater instance with mocked dependencies for testing.

    This fixture combines several mock fixtures to create a testable
    UIUpdater instance with controlled dependencies.

    Args:
        mock_music_controller: Mock of the music controller.
        ui_elements: UIElements instance with mock UI components.
        mock_timer: Mock of QTimer.
        mock_message_manager: Mock of MessageManager.

    Returns:
        UIUpdater: An instance of UIUpdater with mocked dependencies.
    """
    parent = MagicMock()
    updater = UIUpdater(mock_music_controller, ui_elements, parent)
    return updater


class TestUIUpdater:
    """
    Tests for the UIUpdater class.

    This test class contains methods to test various functionalities
    of the UIUpdater class, including initialization, slider updates,
    and song information handling.
    """

    def test_initialization(self, ui_updater, mock_timer):
        """
        Test that UIUpdater initializes correctly.

        Verifies that UIUpdater sets up the initial state correctly,
        including setting up and starting the timer.

        Args:
            ui_updater: The UIUpdater instance to test.
            mock_timer: The mock timer to verify interactions with.
        """
        assert ui_updater.is_slider_moving is False
        mock_timer.setInterval.assert_called_with(1000)
        mock_timer.timeout.connect.assert_called()
        mock_timer.start.assert_called()

    def test_update_slider_when_stopped(self, ui_updater):
        """
        Test that slider doesn't update when player is stopped.

        Verifies that UIUpdater doesn't update the slider position
        when the music controller is in the stopped state.

        Args:
            ui_updater: The UIUpdater instance to test.
        """
        ui_updater.music_controller.is_stopped = True
        ui_updater.update_slider()
        assert not ui_updater.slider.setValue.called

    def test_update_slider_when_slider_moving(self, ui_updater):
        """
        Test that slider doesn't update when it's being moved by user.

        Verifies that UIUpdater doesn't update the slider position when
        is_slider_moving flag is True, which indicates user interaction.

        Args:
            ui_updater: The UIUpdater instance to test.
        """
        ui_updater.is_slider_moving = True
        ui_updater.update_slider()
        assert not ui_updater.slider.setValue.called

    def test_update_slider_playing(self, ui_updater):
        """
        Test slider updates correctly when media is playing.

        Verifies that the slider and time label are updated correctly
        based on the current position and duration of the playing media.

        Args:
            ui_updater: The UIUpdater instance to test.
        """
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
        """
        Test updating song info with valid metadata.

        Verifies that UIUpdater correctly extracts and displays song information
        when the audio file has valid metadata tags.

        Args:
            ui_updater: The UIUpdater instance to test.
            mock_file: Mock of the mutagen.File class.
        """
        song_path = "test_song.mp3"
        mock_audio = MagicMock()
        tags_dict = {
            "TIT2": "Test Title",
            "TPE1": "Test Artist",
            "TALB": "Test Album",
        }
        mock_audio.tags.get.side_effect = tags_dict.get
        mock_audio.info.length = 185
        mock_file.return_value = mock_audio
        ui_updater.update_current_song_info(song_path)
        ui_updater.song_info.title.setText.assert_called_once_with("Test Title")
        ui_updater.song_info.artist.setText.assert_called_once_with("Test Artist")
        ui_updater.song_info.album.setText.assert_called_once_with("Test Album")
        ui_updater.song_info.duration.setText.assert_called_once_with("0:03:05")

    def test_update_current_song_info_no_tags(self, ui_updater, mock_file):
        """
        Test updating song info with no metadata tags.

        Verifies that UIUpdater handles files without metadata tags correctly
        by displaying default values and extracting information from the filename.

        Args:
            ui_updater: The UIUpdater instance to test.
            mock_file: Mock of the mutagen.File class.
        """
        song_path = "test_song.mp3"
        filename = os.path.basename(song_path)
        mock_audio = MagicMock()
        mock_audio.tags = None
        mock_audio.info.length = 240
        mock_file.return_value = mock_audio
        ui_updater.update_current_song_info(song_path)
        ui_updater.song_info.title.setText.assert_called_once_with(filename)
        ui_updater.song_info.artist.setText.assert_called_once_with("Unknown Artist")
        ui_updater.song_info.album.setText.assert_called_once_with("Unknown Album")
        ui_updater.song_info.duration.setText.assert_called_once_with("0:04:00")

    def test_update_current_song_info_error(
        self, ui_updater, mock_file, mock_message_manager
    ):
        """
        Test handling of errors when updating song info.

        Verifies that UIUpdater correctly handles errors that occur when
        trying to read metadata, showing error messages and falling back
        to default values.

        Args:
            ui_updater: The UIUpdater instance to test.
            mock_file: Mock of the mutagen.File class.
            mock_message_manager: Mock of the MessageManager class.
        """
        song_path = "test_song.mp3"
        mock_file.side_effect = OSError("Test error")
        ui_updater.update_current_song_info(song_path)
        mock_message_manager.show_critical.assert_called_once()
        ui_updater.song_info.title.setText.assert_called_once_with(
            os.path.basename(song_path)
        )
        ui_updater.song_info.artist.setText.assert_called_once_with("Unknown Artist")
        ui_updater.song_info.album.setText.assert_called_once_with("Unknown Album")
        ui_updater.song_info.duration.setText.assert_called_once_with("0:00:00")

    def test_clear_song_info(self, ui_updater):
        """
        Test clearing song information.

        Verifies that UIUpdater correctly clears all song information
        fields and resets the slider and time label.

        Args:
            ui_updater: The UIUpdater instance to test.
        """
        ui_updater.clear_song_info()
        ui_updater.song_info.title.setText.assert_called_once_with("")
        ui_updater.song_info.artist.setText.assert_called_once_with("")
        ui_updater.song_info.album.setText.assert_called_once_with("")
        ui_updater.song_info.duration.setText.assert_called_once_with("")
        ui_updater.time_label.setText.assert_called_once_with("00:00:00 / 00:00:00")
        ui_updater.slider.setValue.assert_called_once_with(0)


class TestSongInfoLabels:
    """
    Tests for the SongInfoLabels class.

    This test class contains methods to verify the correct initialization
    and behavior of the SongInfoLabels class.
    """

    def test_initialization(self):
        """
        Test that SongInfoLabels initializes correctly.

        Verifies that the SongInfoLabels correctly stores references
        to the provided label widgets.

        Returns:
            None
        """
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
    """
    Tests for the MessageManager class.

    This test class contains methods to verify the correct behavior
    of the different message display methods in the MessageManager class.
    """

    @patch("utils.message_manager.QMessageBox")
    def test_show_info(self, mock_qmessagebox):
        """
        Test showing an info message.

        Verifies that the show_info method correctly calls the QMessageBox
        information dialog with the provided parameters.

        Args:
            mock_qmessagebox: Mock of the QMessageBox class.

        Returns:
            None
        """
        parent = MagicMock()
        title = "Info Title"
        message = "Info Message"
        mgr = MessageManager()
        mgr.show_info(parent, title, message)
        mock_qmessagebox.information.assert_called_once_with(parent, title, message)

    @patch("utils.message_manager.QMessageBox")
    def test_show_warning(self, mock_qmessagebox):
        """
        Test showing a warning message.

        Verifies that the show_warning method correctly calls the QMessageBox
        warning dialog with the provided parameters.

        Args:
            mock_qmessagebox: Mock of the QMessageBox class.

        Returns:
            None
        """
        parent = MagicMock()
        title = "Warning Title"
        message = "Warning Message"
        mgr = MessageManager()
        mgr.show_warning(parent, title, message)
        mock_qmessagebox.warning.assert_called_once_with(parent, title, message)

    @patch("utils.message_manager.QMessageBox")
    def test_show_critical(self, mock_qmessagebox):
        """
        Test showing a critical message without exception.

        Verifies that the show_critical method correctly calls the QMessageBox
        critical dialog with the provided parameters when no exception is provided.

        Args:
            mock_qmessagebox: Mock of the QMessageBox class.

        Returns:
            None
        """
        parent = MagicMock()
        title = "Error Title"
        message = "Error Message"
        mgr = MessageManager()
        mgr.show_critical(parent, title, message)
        mock_qmessagebox.critical.assert_called_once_with(parent, title, message)

    @patch("utils.message_manager.QMessageBox")
    def test_show_critical_with_exception(self, mock_qmessagebox):
        """
        Test showing a critical message with exception details.

        Verifies that the show_critical method correctly calls the QMessageBox
        critical dialog with the provided parameters and includes exception details
        when an exception is provided.

        Args:
            mock_qmessagebox: Mock of the QMessageBox class.

        Returns:
            None
        """
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
        """
        Test showing a question message.

        Verifies that the show_question method correctly calls the QMessageBox
        question dialog with the provided parameters and appropriate buttons,
        and returns the result from the dialog.

        Args:
            mock_qmessagebox: Mock of the QMessageBox class.

        Returns:
            None
        """
        parent = MagicMock()
        title = "Question Title"
        message = "Question Message"
        mock_qmessagebox.Yes = 16384
        mock_qmessagebox.No = 65536
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

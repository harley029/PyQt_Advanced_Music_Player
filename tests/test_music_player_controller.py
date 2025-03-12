# pylint: disable=redefined-outer-name
from unittest.mock import MagicMock, patch
import pytest

from PyQt5.QtMultimedia import QMediaPlayer

from controllers.music_player_controller import MusicPlayerController


@pytest.fixture
def player_controller():
    """
    Creates a MusicPlayerController instance with a mocked QMediaPlayer.

    Returns:
        MusicPlayerController: A controller instance with the _player attribute
                              replaced with a MagicMock object that simulates
                              a QMediaPlayer.
    """
    controller = MusicPlayerController()
    controller._player = MagicMock(spec=QMediaPlayer)
    return controller


@pytest.fixture
def sample_mp3(tmp_path):
    """
    Creates a dummy MP3 file for testing.

    Args:
        tmp_path (Path): Pytest fixture that provides a temporary directory path.

    Returns:
        str: The absolute path to the created dummy MP3 file.
    """
    mp3_path = tmp_path / "test_song.mp3"
    mp3_path.write_bytes(b"dummy mp3 content")
    return str(mp3_path)


class TestMusicPlayerController:
    """
    Tests for the MusicPlayerController class.

    This test suite verifies the functionality of the MusicPlayerController class,
    including initialization, playback control, state management, and error handling.
    """

    def test_initialization(self):
        """
        Test that controller initializes with correct default values.

        Verifies:
            - The controller creates a QMediaPlayer instance
            - All state flags are initialized to their correct default values
            - The current_song_path is initially None
        """
        controller = MusicPlayerController()
        assert isinstance(controller._player, QMediaPlayer)
        assert controller.is_shuffled is False
        assert controller.is_looped is False
        assert controller.is_stopped is False
        assert controller.current_song_path is None

    def test_set_volume(self, player_controller):
        """
        Test volume setting functionality.

        Args:
            player_controller (MusicPlayerController): Fixture providing a controller with mocked player.

        Verifies:
            - The controller correctly passes volume values to the underlying QMediaPlayer
            - Volume can be set to various levels (0, 50, 100)
        """
        volumes = [0, 50, 100]
        for volume in volumes:
            player_controller.set_volume(volume)
            player_controller._player.setVolume.assert_called_with(volume)

    def test_current_volume(self, player_controller):
        """
        Test getting current volume level.

        Args:
            player_controller (MusicPlayerController): Fixture providing a controller with mocked player.

        Verifies:
            - The controller correctly retrieves the volume from the underlying QMediaPlayer
            - The volume method is called exactly once
        """
        player_controller._player.volume.return_value = 75
        assert player_controller.current_volume() == 75
        player_controller._player.volume.assert_called_once()

    def test_play_song_with_valid_path(self, player_controller, sample_mp3):
        """
        Test playing a song with a valid file path.

        Args:
            player_controller (MusicPlayerController): Fixture providing a controller with mocked player.
            sample_mp3 (str): Path to a test MP3 file.

        Verifies:
            - The controller updates current_song_path
            - The controller calls setMedia on the underlying player
            - The controller calls play on the underlying player
        """
        player_controller.play_song(sample_mp3)
        assert player_controller.current_song_path == sample_mp3
        player_controller._player.setMedia.assert_called_once()
        player_controller._player.play.assert_called_once()

    def test_play_song_with_invalid_path(self, player_controller):
        """
        Test that playing a song with an invalid path does nothing.

        Args:
            player_controller (MusicPlayerController): Fixture providing a controller with mocked player.

        Verifies:
            - The controller does not call setMedia or play when given an invalid path
            - The current_song_path remains None
        """
        player_controller.play_song("/nonexistent/path/song.mp3")
        player_controller._player.setMedia.assert_not_called()
        player_controller._player.play.assert_not_called()
        assert player_controller.current_song_path is None

    def test_play_song_with_empty_path(self, player_controller):
        """
        Test that playing a song with an empty path does nothing.

        Args:
            player_controller (MusicPlayerController): Fixture providing a controller with mocked player.

        Verifies:
            - The controller does not call setMedia or play when given an empty path
            - The current_song_path remains None
        """
        player_controller.play_song("")
        player_controller._player.setMedia.assert_not_called()
        player_controller._player.play.assert_not_called()
        assert player_controller.current_song_path is None

    def test_play_song_exception_handling(self, player_controller, sample_mp3):
        """
        Test exception handling when playing a song.

        Args:
            player_controller (MusicPlayerController): Fixture providing a controller with mocked player.
            sample_mp3 (str): Path to a test MP3 file.

        Verifies:
            - Exceptions from setMedia are propagated correctly

        Raises:
            Exception: Re-raises the exception from setMedia
        """
        player_controller._player.setMedia.side_effect = Exception("Test error")
        with pytest.raises(Exception):
            player_controller.play_song(sample_mp3)

    def test_stop_song_when_playing(self, player_controller):
        """
        Test stopping a song when it is playing.

        Args:
            player_controller (MusicPlayerController): Fixture providing a controller with mocked player.

        Verifies:
            - The controller calls stop on the underlying player when a song is playing
        """
        player_controller._player.state.return_value = QMediaPlayer.PlayingState
        player_controller.stop_song()
        player_controller._player.stop.assert_called_once()

    def test_stop_song_when_not_playing(self, player_controller):
        """
        Test that stopping has no effect when no song is playing.

        Args:
            player_controller (MusicPlayerController): Fixture providing a controller with mocked player.

        Verifies:
            - The controller does not call stop on the underlying player when no song is playing
        """
        player_controller._player.state.return_value = QMediaPlayer.StoppedState
        player_controller.stop_song()
        player_controller._player.stop.assert_not_called()

    def test_pause_song_when_playing(self, player_controller):
        """
        Test pausing a song when it is playing.

        Args:
            player_controller (MusicPlayerController): Fixture providing a controller with mocked player.

        Verifies:
            - The controller calls pause on the underlying player when a song is playing
        """
        player_controller._player.state.return_value = QMediaPlayer.PlayingState
        player_controller.pause_song()
        player_controller._player.pause.assert_called_once()

    def test_pause_song_when_not_playing(self, player_controller):
        """
        Test that pausing has no effect when no song is playing.

        Args:
            player_controller (MusicPlayerController): Fixture providing a controller with mocked player.

        Verifies:
            - The controller does not call pause on the underlying player when no song is playing
        """
        player_controller._player.state.return_value = QMediaPlayer.StoppedState
        player_controller.pause_song()
        player_controller._player.pause.assert_not_called()

    def test_resume_song_when_paused(self, player_controller):
        """
        Test resuming a song when it is paused.

        Args:
            player_controller (MusicPlayerController): Fixture providing a controller with mocked player.

        Verifies:
            - The controller calls play on the underlying player when a song is paused
        """
        player_controller._player.state.return_value = QMediaPlayer.PausedState
        player_controller.resume_song()
        player_controller._player.play.assert_called_once()

    def test_resume_song_when_not_paused(self, player_controller):
        """
        Test that resuming has no effect when song is not paused.

        Args:
            player_controller (MusicPlayerController): Fixture providing a controller with mocked player.

        Verifies:
            - The controller does not call play on the underlying player when a song is not paused
        """
        player_controller._player.state.return_value = QMediaPlayer.StoppedState
        player_controller.resume_song()
        player_controller._player.play.assert_not_called()

    def test_is_playing(self, player_controller):
        """
        Test is_playing returns correct boolean value.

        Args:
            player_controller (MusicPlayerController): Fixture providing a controller with mocked player.

        Verifies:
            - The is_playing method returns True when player is in PlayingState
            - The is_playing method returns False when player is in StoppedState

        Returns:
            None
        """
        player_controller._player.state.return_value = QMediaPlayer.PlayingState
        assert player_controller.is_playing() is True
        player_controller._player.state.return_value = QMediaPlayer.StoppedState
        assert player_controller.is_playing() is False

    def test_is_paused(self, player_controller):
        """
        Test is_paused returns correct boolean value.

        Args:
            player_controller (MusicPlayerController): Fixture providing a controller with mocked player.

        Verifies:
            - The is_paused method returns True when player is in PausedState
            - The is_paused method returns False when player is in PlayingState

        Returns:
            None
        """
        player_controller._player.state.return_value = QMediaPlayer.PausedState
        assert player_controller.is_paused() is True
        player_controller._player.state.return_value = QMediaPlayer.PlayingState
        assert player_controller.is_paused() is False

    def test_set_looped(self, player_controller):
        """
        Test setting loop mode.

        Args:
            player_controller (MusicPlayerController): Fixture providing a controller with mocked player.

        Verifies:
            - The is_looped attribute is correctly set to True when loop is enabled
            - The is_looped attribute is correctly set to False when loop is disabled
        """
        player_controller.set_looped(True)
        assert player_controller.is_looped is True
        player_controller.set_looped(False)
        assert player_controller.is_looped is False

    def test_set_shuffled(self, player_controller):
        """
        Test setting shuffle mode.

        Args:
            player_controller (MusicPlayerController): Fixture providing a controller with mocked player.

        Verifies:
            - The is_shuffled attribute is correctly set to True when shuffle is enabled
            - The is_shuffled attribute is correctly set to False when shuffle is disabled
        """
        player_controller.set_shuffled(True)
        assert player_controller.is_shuffled is True
        player_controller.set_shuffled(False)
        assert player_controller.is_shuffled is False

    def test_media_player(self, player_controller):
        """
        Test getting the underlying QMediaPlayer instance.

        Args:
            player_controller (MusicPlayerController): Fixture providing a controller with mocked player.

        Verifies:
            - The media_player method returns the internal _player instance

        Returns:
            None
        """
        media_player = player_controller.media_player()
        assert media_player is player_controller._player

    @patch("controllers.music_player_controller.QMediaContent")
    @patch("controllers.music_player_controller.QUrl")
    def test_media_content_creation(
        self, mock_qurl, mock_media_content, player_controller, sample_mp3
    ):
        """
        Test the creation of QMediaContent with the correct URL.

        Args:
            mock_qurl (MagicMock): Mock for the QUrl class.
            mock_media_content (MagicMock): Mock for the QMediaContent class.
            player_controller (MusicPlayerController): Fixture providing a controller with mocked player.
            sample_mp3 (str): Path to a test MP3 file.

        Verifies:
            - QUrl.fromLocalFile is called with the correct file path
            - QMediaContent is created with the URL returned by QUrl.fromLocalFile
            - setMedia is called with the created QMediaContent object
        """
        mock_url = MagicMock()
        mock_qurl.fromLocalFile.return_value = mock_url
        mock_media = MagicMock()
        mock_media_content.return_value = mock_media
        player_controller.play_song(sample_mp3)
        mock_qurl.fromLocalFile.assert_called_with(sample_mp3)
        mock_media_content.assert_called_with(mock_url)
        player_controller._player.setMedia.assert_called_with(mock_media)

    def test_playback_workflow(self, player_controller, sample_mp3):
        """
        Test a complete playback workflow.

        This test verifies a full playback cycle including play, pause, resume, and stop.

        Args:
            player_controller (MusicPlayerController): Fixture providing a controller with mocked player.
            sample_mp3 (str): Path to a test MP3 file.

        Verifies:
            - Play: The song path is set, media is set, and play is called
            - The player enters PlayingState correctly
            - Pause: The pause method is called and the player enters PausedState
            - Resume: The play method is called again
            - Stop: The stop method is called
        """
        player_controller._player.state.return_value = QMediaPlayer.StoppedState
        player_controller.play_song(sample_mp3)
        assert player_controller.current_song_path == sample_mp3
        player_controller._player.setMedia.assert_called_once()
        player_controller._player.play.assert_called_once()
        player_controller._player.state.return_value = QMediaPlayer.PlayingState
        assert player_controller.is_playing() is True
        player_controller.pause_song()
        player_controller._player.pause.assert_called_once()
        player_controller._player.state.return_value = QMediaPlayer.PausedState
        assert player_controller.is_paused() is True
        player_controller.resume_song()
        assert player_controller._player.play.call_count == 2
        player_controller._player.state.return_value = QMediaPlayer.PlayingState
        player_controller.stop_song()
        player_controller._player.stop.assert_called_once()

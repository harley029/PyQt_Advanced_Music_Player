# pylint: disable=redefined-outer-name
from unittest.mock import MagicMock, patch
import pytest

from PyQt5.QtMultimedia import QMediaPlayer

from controllers.music_player_controller import MusicPlayerController


@pytest.fixture
def player_controller():
    """Creates a MusicPlayerController instance with mocked QMediaPlayer."""
    controller = MusicPlayerController()
    controller._player = MagicMock(spec=QMediaPlayer)
    return controller


@pytest.fixture
def sample_mp3(tmp_path):
    """Creates a dummy MP3 file for testing."""
    mp3_path = tmp_path / "test_song.mp3"
    mp3_path.write_bytes(b"dummy mp3 content")
    return str(mp3_path)


class TestMusicPlayerController:
    """Tests for the MusicPlayerController class."""

    def test_initialization(self):
        """Test that controller initializes with correct default values."""
        controller = MusicPlayerController()

        assert isinstance(controller._player, QMediaPlayer)
        assert controller.is_shuffled is False
        assert controller.is_looped is False
        assert controller.is_stopped is False
        assert controller.current_song_path is None

    def test_set_volume(self, player_controller):
        """Test volume setting functionality."""
        # Test with various volume levels
        volumes = [0, 50, 100]

        for volume in volumes:
            player_controller.set_volume(volume)
            player_controller._player.setVolume.assert_called_with(volume)

    def test_current_volume(self, player_controller):
        """Test getting current volume level."""
        player_controller._player.volume.return_value = 75

        assert player_controller.current_volume() == 75
        player_controller._player.volume.assert_called_once()

    def test_play_song_with_valid_path(self, player_controller, sample_mp3):
        """Test playing a song with a valid file path."""
        player_controller.play_song(sample_mp3)

        assert player_controller.current_song_path == sample_mp3
        player_controller._player.setMedia.assert_called_once()
        player_controller._player.play.assert_called_once()

    def test_play_song_with_invalid_path(self, player_controller):
        """Test that playing a song with an invalid path does nothing."""
        player_controller.play_song("/nonexistent/path/song.mp3")

        player_controller._player.setMedia.assert_not_called()
        player_controller._player.play.assert_not_called()
        assert player_controller.current_song_path is None

    def test_play_song_with_empty_path(self, player_controller):
        """Test that playing a song with an empty path does nothing."""
        player_controller.play_song("")

        player_controller._player.setMedia.assert_not_called()
        player_controller._player.play.assert_not_called()
        assert player_controller.current_song_path is None

    def test_play_song_exception_handling(self, player_controller, sample_mp3):
        """Test exception handling when playing a song."""
        player_controller._player.setMedia.side_effect = Exception("Test error")

        with pytest.raises(Exception):
            player_controller.play_song(sample_mp3)

    def test_stop_song_when_playing(self, player_controller):
        """Test stopping a song when it is playing."""
        player_controller._player.state.return_value = QMediaPlayer.PlayingState

        player_controller.stop_song()

        player_controller._player.stop.assert_called_once()

    def test_stop_song_when_not_playing(self, player_controller):
        """Test that stopping has no effect when no song is playing."""
        player_controller._player.state.return_value = QMediaPlayer.StoppedState

        player_controller.stop_song()

        player_controller._player.stop.assert_not_called()

    def test_pause_song_when_playing(self, player_controller):
        """Test pausing a song when it is playing."""
        player_controller._player.state.return_value = QMediaPlayer.PlayingState

        player_controller.pause_song()

        player_controller._player.pause.assert_called_once()

    def test_pause_song_when_not_playing(self, player_controller):
        """Test that pausing has no effect when no song is playing."""
        player_controller._player.state.return_value = QMediaPlayer.StoppedState

        player_controller.pause_song()

        player_controller._player.pause.assert_not_called()

    def test_resume_song_when_paused(self, player_controller):
        """Test resuming a song when it is paused."""
        player_controller._player.state.return_value = QMediaPlayer.PausedState

        player_controller.resume_song()

        player_controller._player.play.assert_called_once()

    def test_resume_song_when_not_paused(self, player_controller):
        """Test that resuming has no effect when song is not paused."""
        player_controller._player.state.return_value = QMediaPlayer.StoppedState

        player_controller.resume_song()

        player_controller._player.play.assert_not_called()

    def test_is_playing(self, player_controller):
        """Test is_playing returns correct boolean value."""
        # Test when song is playing
        player_controller._player.state.return_value = QMediaPlayer.PlayingState
        assert player_controller.is_playing() is True

        # Test when song is not playing
        player_controller._player.state.return_value = QMediaPlayer.StoppedState
        assert player_controller.is_playing() is False

    def test_is_paused(self, player_controller):
        """Test is_paused returns correct boolean value."""
        # Test when song is paused
        player_controller._player.state.return_value = QMediaPlayer.PausedState
        assert player_controller.is_paused() is True

        # Test when song is not paused
        player_controller._player.state.return_value = QMediaPlayer.PlayingState
        assert player_controller.is_paused() is False

    def test_set_looped(self, player_controller):
        """Test setting loop mode."""
        # Test enabling loop mode
        player_controller.set_looped(True)
        assert player_controller.is_looped is True

        # Test disabling loop mode
        player_controller.set_looped(False)
        assert player_controller.is_looped is False

    def test_set_shuffled(self, player_controller):
        """Test setting shuffle mode."""
        # Test enabling shuffle mode
        player_controller.set_shuffled(True)
        assert player_controller.is_shuffled is True

        # Test disabling shuffle mode
        player_controller.set_shuffled(False)
        assert player_controller.is_shuffled is False

    def test_media_player(self, player_controller):
        """Test getting the underlying QMediaPlayer instance."""
        media_player = player_controller.media_player()
        assert media_player is player_controller._player

    @patch("controllers.music_player_controller.QMediaContent")
    @patch("controllers.music_player_controller.QUrl")
    def test_media_content_creation(
        self, mock_qurl, mock_media_content, player_controller, sample_mp3
    ):
        """Test the creation of QMediaContent with the correct URL."""
        mock_url = MagicMock()
        mock_qurl.fromLocalFile.return_value = mock_url
        mock_media = MagicMock()
        mock_media_content.return_value = mock_media

        player_controller.play_song(sample_mp3)

        mock_qurl.fromLocalFile.assert_called_with(sample_mp3)
        mock_media_content.assert_called_with(mock_url)
        player_controller._player.setMedia.assert_called_with(mock_media)

    def test_playback_workflow(self, player_controller, sample_mp3):
        """Test a complete playback workflow."""
        # Setup initial state
        player_controller._player.state.return_value = QMediaPlayer.StoppedState

        # 1. Play a song
        player_controller.play_song(sample_mp3)
        assert player_controller.current_song_path == sample_mp3
        player_controller._player.setMedia.assert_called_once()
        player_controller._player.play.assert_called_once()

        # 2. Change the player state to playing
        player_controller._player.state.return_value = QMediaPlayer.PlayingState
        assert player_controller.is_playing() is True

        # 3. Pause the song
        player_controller.pause_song()
        player_controller._player.pause.assert_called_once()

        # 4. Change the player state to paused
        player_controller._player.state.return_value = QMediaPlayer.PausedState
        assert player_controller.is_paused() is True

        # 5. Resume the song
        player_controller.resume_song()
        assert (
            player_controller._player.play.call_count == 2
        )  # First call was during play_song

        # 6. Change the player state back to playing
        player_controller._player.state.return_value = QMediaPlayer.PlayingState

        # 7. Stop the song
        player_controller.stop_song()
        player_controller._player.stop.assert_called_once()

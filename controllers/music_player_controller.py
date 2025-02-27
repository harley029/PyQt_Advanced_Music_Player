import os
import logging

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl

from interfaces.interfaces import IMusicPlayerController

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class MusicPlayerController(IMusicPlayerController):
    """
    Controls music playback functionality.

    This class implements the IMusicPlayerController interface and provides methods
    for controlling music playback, including play, pause, stop, volume control,
    and playback mode settings (shuffle and loop).
    """

    def __init__(self):
        """
        Initialize the music player controller.

        Sets up the QMediaPlayer instance and initializes playback state flags.
        """
        self._player = QMediaPlayer()
        self.is_shuffled = False
        self.is_looped = False
        self.is_stopped = False
        self.current_song_path = None

    def set_volume(self, volume: int):
        """
        Set the playback volume.

        Parameters:
            volume: Integer value representing volume level (0-100)
        """
        self._player.setVolume(volume)

    def current_volume(self) -> int:
        """
        Get the current volume level.

        Returns:
            Integer representing current volume level (0-100)
        """
        return self._player.volume()

    def play_song(self, song_path: str):
        """
        Start playing a song from the specified path.

        Validates the path existence before attempting playback. Updates the
        current song path and creates a new media content for playback.

        Parameters:
            song_path: Path to the audio file to be played
        """
        if not song_path or not os.path.exists(song_path):
            return

        try:
            self.current_song_path = song_path
            media = QMediaContent(QUrl.fromLocalFile(song_path))
            self._player.setMedia(media)
            self._player.play()
            logging.info("Playing song: %s", song_path)
        except Exception as e:
            logging.error("Failed to play song %s: %s", song_path, e)
            raise

    def stop_song(self):
        """
        Stop the current playback.

        Only stops if a song is currently playing.
        """
        if self._player.state() == QMediaPlayer.PlayingState:
            self._player.stop()

    def pause_song(self):
        """
        Pause the current playback.

        Only pauses if a song is currently playing.
        """
        if self._player.state() == QMediaPlayer.PlayingState:
            self._player.pause()

    def resume_song(self):
        """
        Resume playback of a paused song.

        Only resumes if a song is currently paused.
        """
        if self._player.state() == QMediaPlayer.PausedState:
            self._player.play()

    def is_playing(self) -> bool:
        """
        Check if a song is currently playing.

        Returns:
            True if a song is playing, False otherwise
        """
        return self._player.state() == QMediaPlayer.PlayingState

    def is_paused(self) -> bool:
        """
        Check if playback is currently paused.

        Returns:
            True if playback is paused, False otherwise
        """
        return self._player.state() == QMediaPlayer.PausedState

    def set_looped(self, looped: bool):
        """
        Set the loop playback mode.

        Parameters:
            looped: True to enable loop mode, False to disable
        """
        self.is_looped = looped

    def set_shuffled(self, shuffled: bool):
        """
        Set the shuffle playback mode.

        Parameters:
            shuffled: True to enable shuffle mode, False to disable
        """
        self.is_shuffled = shuffled

    def media_player(self) -> QMediaPlayer:
        """
        Get the underlying QMediaPlayer instance.

        Returns:
            The QMediaPlayer instance used for playback
        """
        return self._player

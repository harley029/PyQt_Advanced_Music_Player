import os

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl

from interfaces.interfaces import IMusicPlayerController


class MusicPlayerController(IMusicPlayerController):

    def __init__(self):
        self._player = QMediaPlayer()

        self.is_shuffled = False
        self.is_looped = False
        self.is_stopped = False
        self.current_song_path = None

    def set_volume(self, volume: int):
        self._player.setVolume(volume)

    def current_volume(self) -> int:
        return self._player.volume()

    def play_song(self, song_path: str):
        if not song_path or not os.path.exists(song_path):
            return  # можно выводить предупреждение

        self.current_song_path = song_path
        media = QMediaContent(QUrl.fromLocalFile(song_path))
        self._player.setMedia(media)
        self._player.play()

    def stop_song(self):
        if self._player.state() == QMediaPlayer.PlayingState:
            self._player.stop()

    def pause_song(self):
        if self._player.state() == QMediaPlayer.PlayingState:
            self._player.pause()

    def resume_song(self):
        if self._player.state() == QMediaPlayer.PausedState:
            self._player.play()

    def is_playing(self) -> bool:
        return self._player.state() == QMediaPlayer.PlayingState

    def is_paused(self) -> bool:
        return self._player.state() == QMediaPlayer.PausedState

    def set_looped(self, looped: bool):
        self.is_looped = looped

    def set_shuffled(self, shuffled: bool):
        self.is_shuffled = shuffled

    def media_player(self) -> QMediaPlayer:
        return self._player

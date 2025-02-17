import time
from os.path import basename

from PyQt5.QtCore import QTimer
from PyQt5.QtMultimedia import QMediaPlayer

from mutagen import File


class UIUpdater:

    def __init__(
        self,
        music_controller,
        slider,
        time_label,
        current_song_title,
        current_song_artist,
        current_song_album,
        current_song_duration,
    ):
        self.music_controller = music_controller
        self.slider = slider
        self.time_label = time_label
        self.current_song_title = current_song_title
        self.current_song_artist = current_song_artist
        self.current_song_album = current_song_album
        self.current_song_duration = current_song_duration

        self.is_slider_moving = False

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_slider)
        self.timer.start()

    def update_slider(self):
        if self.music_controller.is_stopped or self.is_slider_moving:
            return
        player = self.music_controller.media_player()
        if player.state() == QMediaPlayer.PlayingState:
            self.slider.setMinimum(0)
            duration = player.duration()
            self.slider.setMaximum(duration)
            slider_position = player.position()
            self.slider.setValue(slider_position)
            current_time = time.strftime(
                "%H:%M:%S", time.gmtime(slider_position // 1000)
            )
            total_time = time.strftime("%H:%M:%S", time.gmtime(duration // 1000))
            self.time_label.setText(f"{current_time} / {total_time}")

    def update_current_song_info(self, song_path):
        audio = File(song_path)
        title = audio.tags.get("TIT2") if audio.tags and "TIT2" in audio.tags else basename(self.song_path)
        artist = audio.tags.get("TPE1") if audio.tags and "TPE1" in audio.tags else "Unknown Artist"
        album = audio.tags.get("TALB") if audio.tags and "TALB" in audio.tags else "Unknown Album"
        duration = audio.info.length if audio.info else 0

        self.current_song_title.setText(f"{title}")
        self.current_song_artist.setText(f"{artist}")
        self.current_song_album.setText(f"{album}")
        self.current_song_duration.setText(f"{int(duration // 3600)}:{int((duration % 3600) // 60):02}:{int(duration % 60):02}")

    def clear_song_info(self):
        self.current_song_title.setText("")
        self.current_song_artist.setText("")
        self.current_song_album.setText("")
        self.current_song_duration.setText("")
        self.time_label.setText("00:00:00 / 00:00:00")
        self.slider.setValue(0)

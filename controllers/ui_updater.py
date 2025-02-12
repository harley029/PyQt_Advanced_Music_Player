import time

from PyQt5.QtCore import QTimer
from PyQt5.QtMultimedia import QMediaPlayer


class UIUpdater:
    def __init__(
        self, music_controller, slider, time_label, song_name_label, song_path_label
    ):
        self.music_controller = music_controller
        self.slider = slider
        self.time_label = time_label
        self.song_name_label = song_name_label
        self.song_path_label = song_path_label

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
        from os.path import basename, dirname

        self.song_name_label.setText(basename(song_path))
        self.song_path_label.setText(dirname(song_path))

    def clear_song_info(self):
        self.song_name_label.setText("")
        self.song_path_label.setText("")
        self.time_label.setText("00:00:00 / 00:00:00")
        self.slider.setValue(0)

import time

from PyQt5.QtCore import QTimer
from PyQt5.QtMultimedia import QMediaPlayer

from mutagen import File


class SongInfoLabels:
    """
    Класс для группировки ярлыков, отображающих информацию о песне.
    """

    def __init__(self, title_label, artist_label, album_label, duration_label):
        self.title = title_label
        self.artist = artist_label
        self.album = album_label
        self.duration = duration_label


class UIUpdater:
    """
    Обновляет элементы пользовательского интерфейса для отображения времени воспроизведения и информации о песне.
    """

    def __init__(self, music_controller, slider, time_label, song_info: SongInfoLabels):
        """
        :param music_controller: Контроллер воспроизведения музыки.
        :param slider: Виджет-слайдер для отображения позиции песни.
        :param time_label: Виджет для отображения времени воспроизведения.
        :param song_info: Объект SongInfoLabels, содержащий ярлыки для информации о песне.
        """
        self.music_controller = music_controller
        self.slider = slider
        self.time_label = time_label
        self.song_info = song_info

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
        title = (
            audio.tags.get("TIT2")
            if audio.tags and "TIT2" in audio.tags
            else song_path.split("/")[-1]
        )
        artist = (
            audio.tags.get("TPE1")
            if audio.tags and "TPE1" in audio.tags
            else "Unknown Artist"
        )
        album = (
            audio.tags.get("TALB")
            if audio.tags and "TALB" in audio.tags
            else "Unknown Album"
        )
        duration = audio.info.length if audio.info else 0

        self.song_info.title.setText(f"{title}")
        self.song_info.artist.setText(f"{artist}")
        self.song_info.album.setText(f"{album}")
        self.song_info.duration.setText(
            f"{int(duration // 3600)}:{int((duration % 3600) // 60):02}:{int(duration % 60):02}"
        )

    def clear_song_info(self):
        self.song_info.title.setText("")
        self.song_info.artist.setText("")
        self.song_info.album.setText("")
        self.song_info.duration.setText("")
        self.time_label.setText("00:00:00 / 00:00:00")
        self.slider.setValue(0)

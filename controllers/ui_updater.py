import os
import time

from PyQt5.QtCore import QTimer
from PyQt5.QtMultimedia import QMediaPlayer

from mutagen import File

from utils.message_manager import messanger
from utils import messages as msg


class SongInfoLabels:
    """
    A class for grouping labels that display song information.

    This class stores references to UI labels that show various pieces of song metadata
    like title, artist, album, and duration.
    """

    def __init__(self, title_label, artist_label, album_label, duration_label):
        """
        Initialize a SongInfoLabels object with the provided UI label widgets.

        Parameters:
            title_label: Label widget that displays the song title
            artist_label: Label widget that displays the artist name
            album_label: Label widget that displays the album name
            duration_label: Label widget that displays the song duration
        """
        self.title = title_label
        self.artist = artist_label
        self.album = album_label
        self.duration = duration_label


class UIUpdater:
    """
    Updates user interface elements to display playback time and song information.

    This class manages the synchronization between the music player state and
    the UI elements, handling slider position updates, time display, and metadata presentation.
    """

    def __init__(self, music_controller, slider, time_label, song_info: SongInfoLabels, parent=None):
        """
        Initialize a UIUpdater object with the necessary components.

        Parameters:
            music_controller: The music playback controller
            slider: Slider widget to display and control song position
            time_label: Label widget to display playback time
            song_info: SongInfoLabels object containing labels for song metadata
        """
        self.music_controller = music_controller
        self.slider = slider
        self.time_label = time_label
        self.song_info = song_info
        self.parent = parent

        self.is_slider_moving = False

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_slider)
        self.timer.start()

    def update_slider(self):
        """
        Update the position slider and time label based on the current playback state.

        This method is called periodically by the timer to reflect the current
        playback position in the UI. It updates the slider position and displays
        current/total playback time.
        """
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
        """
        Update the UI labels with metadata from the current song.

        This method extracts metadata (title, artist, album, duration) from the
        audio file and updates the corresponding UI labels.

        Parameters:
            song_path: Path to the audio file being played
        """
        title = os.path.basename(song_path)  # Запасное значение
        artist = "Unknown Artist"
        album = "Unknown Album"
        duration = 0

        try:
            audio = File(song_path)
            if audio and audio.tags:
                title = audio.tags.get("TIT2", title)
                artist = audio.tags.get("TPE1", artist)
                album = audio.tags.get("TALB", album)
            duration = audio.info.length if audio and audio.info else 0
        except Exception as e:
            messanger.show_critical(
                self.parent,
                msg.TTL_ERR,
                f"Failed to load metadata for {song_path}: {e}",
            )
        self.song_info.title.setText(f"{title}")
        self.song_info.artist.setText(f"{artist}")
        self.song_info.album.setText(f"{album}")
        self.song_info.duration.setText(
            f"{int(duration // 3600)}:{int((duration % 3600) // 60):02}:{int(duration % 60):02}"
        )

    def clear_song_info(self):
        """
        Clear all song information and reset UI elements.

        This method resets all labels and the slider to their default states,
        typically called when playback stops or before loading a new song.
        """
        self.song_info.title.setText("")
        self.song_info.artist.setText("")
        self.song_info.album.setText("")
        self.song_info.duration.setText("")
        self.time_label.setText("00:00:00 / 00:00:00")
        self.slider.setValue(0)

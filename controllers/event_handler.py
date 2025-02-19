import os
from typing import Optional

from PyQt5.QtWidgets import QMessageBox, QFileDialog, QListWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer

from interfaces.navigation.navigation import (
    NormalNavigationStrategy,
    RandomNavigationStrategy,
    LoopingNavigationStrategy,
)
from interfaces.interfaces import INavigationStrategy
from utils import messages as msg
from controllers.ui_updater import UIUpdater
from controllers.music_player_controller import MusicPlayerController


class PlaybackHandler:
    """
    Handles playback operations: play, pause, and stop.

    This class encapsulates all logic related to music playback control,
    working in conjunction with the music controller and UI updater.
    """

    def __init__(self, music_controller: MusicPlayerController, ui_updater: UIUpdater):
        """
        Initialize the PlaybackHandler.

        Args:
            music_controller: Object implementing IMusicPlayerController interface
            ui_updater: Object responsible for UI updates (e.g., UIUpdater)
        """
        self.music_controller = music_controller
        self.ui_updater = ui_updater

    def play(self, song_path: str) -> None:
        """
        Start playing a song and update the UI accordingly.

        Args:
            song_path: File path to the song to be played
        """
        self.music_controller.play_song(song_path)
        self.ui_updater.update_current_song_info(song_path)

    def pause(self) -> None:
        """
        Toggle between pause and resume states.

        If the song is playing, it will be paused.
        If the song is paused, it will be resumed.
        """
        if self.music_controller.is_playing():
            self.music_controller.pause_song()
        elif self.music_controller.is_paused():
            self.music_controller.resume_song()

    def stop(self) -> None:
        """
        Stop the current playback and clear song information from UI.
        """
        self.music_controller.stop_song()
        self.ui_updater.clear_song_info()


class NavigationHandler:
    """
    Handles song list navigation (next, previous) using the Strategy pattern.

    This class manages different navigation strategies (normal, random, looping)
    and delegates the actual navigation logic to the current strategy.
    """

    def __init__(self, navigation_strategy: Optional[INavigationStrategy] = None):
        """
        Initialize the NavigationHandler.

        Args:
            navigation_strategy: Initial navigation strategy. Defaults to NormalNavigationStrategy
                               if none is provided
        """
        self.navigation_strategy = navigation_strategy or NormalNavigationStrategy()

    def set_strategy(self, strategy: INavigationStrategy) -> None:
        """
        Set a new navigation strategy.

        Args:
            strategy: New strategy implementing INavigationStrategy interface
        """
        self.navigation_strategy = strategy

    def get_next_index(self, current_index: int, count: int) -> int:
        """
        Get the next song index based on current strategy.

        Args:
            current_index: Current song index
            count: Total number of songs

        Returns:
            Next song index according to current navigation strategy
        """
        return self.navigation_strategy.get_next_index(current_index, count)

    def get_previous_index(self, current_index: int, count: int) -> int:
        """
        Get the previous song index based on current strategy.

        Args:
            current_index: Current song index
            count: Total number of songs

        Returns:
            Previous song index according to current navigation strategy
        """
        return self.navigation_strategy.get_previous_index(current_index, count)


class EventHandlerConfig:
    """
    Configuration container for EventHandler dependencies.

    Centralizes all dependencies required by the EventHandler to function,
    making initialization and dependency management cleaner.
    """

    def __init__(
        self,
        ui,
        music_controller,
        playlist_manager,
        favourites_manager,
        ui_updater,
        db_manager,
    ):
        """
        Initialize the configuration container.

        Args:
            ui: Main UI component
            music_controller: Controller for music playback
            playlist_manager: Manager for playlist operations
            favourites_manager: Manager for favorites operations
            ui_updater: Component for updating UI elements
            db_manager: Manager for database operations
        """
        self.ui = ui
        self.music_controller = music_controller
        self.playlist_manager = playlist_manager
        self.favourites_manager = favourites_manager
        self.ui_updater = ui_updater
        self.db_manager = db_manager


class EventHandler:
    """
    Main event handler that aggregates specialized handlers.

    Delegates playback, navigation, and UI update actions to appropriate classes.
    Manages all user interactions with the music player interface.
    """

    def __init__(self, config: EventHandlerConfig):
        """
        Initialize the EventHandler with provided configuration.

        Args:
            config: EventHandlerConfig instance containing all required dependencies
        """
        self.ui = config.ui
        self.music_controller = config.music_controller
        self.playlist_manager = config.playlist_manager
        self.favourites_manager = config.favourites_manager
        self.ui_updater = config.ui_updater
        self.db_manager = config.db_manager
        self.playback_handler = PlaybackHandler(self.music_controller, self.ui_updater)
        self.navigation_handler = NavigationHandler()
        self.setup_button_signals()

    def setup_button_signals(self):
        """
        Set up all button signal connections for the UI.

        Connects UI buttons to their respective handler methods for:
        - Song list operations
        - Favorites operations
        - Playlist operations
        - Playback controls
        - Media status changes
        """
        # Кнопки на вкладке Song List
        self.ui.add_songs_btn.clicked.connect(self.on_add_songs_clicked)
        self.ui.delete_selected_btn.clicked.connect(
            lambda: self.on_delete_selected_song_clicked(db_table=None)
        )
        self.ui.delete_all_songs_btn.clicked.connect(
            lambda: self.on_clear_list_clicked(db_table=None)
        )
        # Кнопки на вкладке Favourites
        self.ui.delete_selected_favourite_btn.clicked.connect(
            self.favourites_manager.remove_selected_favourite
        )
        self.ui.delete_all_favourites_btn.clicked.connect(
            self.favourites_manager.clear_favourites
        )
        # Кнопки на вкладке Playlist
        self.ui.new_playlist_btn.clicked.connect(
            lambda: self.playlist_manager.create_playlist(self.ui)
        )
        self.ui.remove_selected_playlist_btn.clicked.connect(
            lambda: self.playlist_manager.remove_playlist(self.ui)
        )
        self.ui.remove_all_playlists_btn.clicked.connect(
            lambda: self.playlist_manager.remove_all_playlists(self.ui)
        )
        self.ui.load_selected_playlist_btn.clicked.connect(
            lambda: self.playlist_manager.load_playlist_into_widget(self.ui)
        )
        # Кнопки добавления песен в списки
        self.ui.add_to_fav_btn.clicked.connect(
            self.favourites_manager.add_to_favourites
        )
        self.ui.add_to_playlist_btn.clicked.connect(
            lambda: self.playlist_manager.add_song_to_playlist(self.ui)
        )

        # Управление воспроизведением
        self.ui.play_btn.clicked.connect(self.on_play_clicked)
        self.ui.pause_btn.clicked.connect(self.on_pause_clicked)
        self.ui.stop_btn.clicked.connect(self.on_stop_clicked)
        self.ui.next_btn.clicked.connect(
            lambda: self.on_next_previous_clicked(direction="forward")
        )
        self.ui.previous_btn.clicked.connect(
            lambda: self.on_next_previous_clicked(direction="buckward")
        )
        self.ui.loop_one_btn.clicked.connect(self.on_loop_clicked)
        self.ui.shuffle_songs_btn.clicked.connect(self.on_shuffle_clicked)
        self.ui.volume_dial.valueChanged.connect(self.on_volume_clicked)

        # Сигналы управления двойными кликами по спискам песен, плейлистов
        self.ui.loaded_songs_listWidget.itemDoubleClicked.connect(self.on_play_clicked)
        self.ui.favourites_listWidget.itemDoubleClicked.connect(self.on_play_clicked)
        self.ui.playlists_listWidget.itemDoubleClicked.connect(
            lambda: self.playlist_manager.load_playlist_into_widget(self.ui)
        )

        # Служебные сигналы
        self.music_controller.media_player().mediaStatusChanged.connect(
            self.handle_media_status
        )

    def get_current_list_widget(self):
        """
        Get the currently active list widget based on selected tab.

        Returns:
            Active QListWidget or None if no valid widget is selected
        """
        idx = self.ui.stackedWidget.currentIndex()
        if idx == 0:
            return self.ui.loaded_songs_listWidget
        if idx == 1:
            return self.ui.playlists_listWidget
        if idx == 2:
            return self.ui.favourites_listWidget
        return None

    def on_add_songs_clicked(self):
        """
        Handle adding new songs to the playlist.

        Opens a file dialog for song selection and adds selected songs
        to the current list widget.
        """
        file_names, _ = QFileDialog.getOpenFileNames(
            self.ui,
            caption="Add Songs",
            directory="",
            filter="Supported Files (*.mp3; *.mpeg; *.ogg; *.m4a; *.MP3; *.wma; *.acc; *.amr)",
        )
        if file_names:
            for file_name in file_names:
                item = QListWidgetItem(
                    QIcon(":/img/utils/images/MusicListItem.png"),
                    os.path.basename(file_name),
                )
                item.setData(Qt.UserRole, file_name)
                self.ui.loaded_songs_listWidget.addItem(item)
        else:
            QMessageBox.information(self.ui, msg.TTL_INF, msg.MSG_NO_FILES_SEL)

    def on_delete_selected_song_clicked(self, db_table=None):
        """
        Handle deletion of selected song from current list.

        Args:
            db_table: Optional database table name. If provided, song will also be
                     removed from the database.

        Raises:
            QMessageBox.critical: If there's an error during deletion
        """
        try:
            list_widget = self.get_current_list_widget()
            if list_widget is None or list_widget.count() == 0:
                QMessageBox.information(self.ui, msg.TTL_ATT, msg.MSG_NO_SONG_TO_DEL)
                return
            items = list_widget.selectedItems()
            if not items:
                QMessageBox.information(self.ui, msg.TTL_ATT, msg.MSG_NO_SONG_SEL)
                return
            item = list_widget.currentItem()
            current_song = item.data(Qt.UserRole)
            # Проверяем, не играет ли сейчас эта песня
            current_media = self.music_controller.media_player().media()
            current_song_url = current_media.canonicalUrl().toLocalFile()
            was_playing = (
                self.music_controller.media_player().state()
                == QMediaPlayer.PlayingState
            )
            if current_song_url == current_song:
                self.on_stop_clicked()
            # Удаление из базы и виджета
            if db_table is None:
                db_table = self.ui.current_playlist
            if db_table:
                self.ui.db_manager.delete_song(db_table, current_song)
            row = list_widget.row(item)
            list_widget.takeItem(row)
            # Запускаем следующую песню
            if list_widget.count() > 0:
                new_selection = row % list_widget.count()
                list_widget.setCurrentRow(new_selection)
                if was_playing:
                    self.on_play_clicked()
                else:
                    self.on_stop_clicked()
        except Exception as e:
            QMessageBox.critical(self.ui, msg.TTL_ERR, f"{msg.MSG_SONG_DEL_ERR} {e}")

    def on_clear_list_clicked(self, db_table=None):
        """
        Handle clearing of entire current list.

        Args:
            db_table: Optional database table name. If provided, all songs will also be
                     removed from the database.

        Raises:
            QMessageBox.critical: If there's an error during clearing
        """
        try:
            list_widget = self.get_current_list_widget()
            if list_widget is None or list_widget.count() == 0:
                QMessageBox.information(self.ui, msg.TTL_ATT, msg.MSG_NO_SONG_TO_DEL)
                return

            question = QMessageBox.question(
                self.ui,
                msg.TTL_SONG_DEL_QUEST,
                msg.MSG_SONG_DEL_QUEST,
                QMessageBox.Yes | QMessageBox.Cancel,
                QMessageBox.Cancel,
            )
            if question == QMessageBox.Yes:
                self.on_stop_clicked()
                list_widget.clear()
                if db_table is None:
                    db_table = self.ui.current_playlist
                if db_table:
                    self.db_manager.delete_all_songs(db_table)
        except Exception as e:
            QMessageBox.critical(
                self.ui, msg.TTL_ERR, f"{msg.MSG_ALL_SONG_DEL_ERR} {e}"
            )

    def on_play_clicked(self):
        """
        Handle play button click or double-click on song.

        Starts playback of selected song in current list widget.

        Raises:
            QMessageBox.critical: If there's an error during playback start
        """
        try:
            list_widget = self.get_current_list_widget()
            if list_widget is None or list_widget.count() == 0:
                QMessageBox.information(self.ui, msg.TTL_ATT, msg.MSG_LST_EMPTY)
                return

            current_item = list_widget.currentItem()
            if not current_item:
                QMessageBox.information(self.ui, msg.TTL_ATT, msg.MSG_NO_SONG_SEL)
                return

            song_path = current_item.data(Qt.UserRole)
            self.playback_handler.play(song_path)
        except Exception as e:
            QMessageBox.critical(self.ui, msg.TTL_ERR, f"{msg.MSG_PLAY_ERR} {e}")

    def on_pause_clicked(self):
        """
        Handle pause button click.

        Toggles between pause and resume states.
        """
        self.playback_handler.pause()

    def on_stop_clicked(self):
        """
        Handle stop button click.

        Stops current playback and clears song information.
        """
        self.playback_handler.stop()

    def on_next_previous_clicked(self, direction: str = "forward"):
        """
        Handle next/previous button clicks.

        Args:
            direction: Navigation direction, either "forward" or "backward"

        Raises:
            QMessageBox.critical: If there's an error during navigation
        """
        try:
            list_widget = self.get_current_list_widget()
            if not list_widget or list_widget.count() == 0:
                QMessageBox.information(self.ui, msg.TTL_ATT, msg.MSG_LST_EMPTY)
                return
            current_index = list_widget.currentRow()
            count = list_widget.count()

            if direction == "forward":
                new_index = self.navigation_handler.get_next_index(current_index, count)
            elif direction == "buckward":
                new_index = self.navigation_handler.get_previous_index(
                    current_index, count
                )
            else:
                new_index = current_index

            list_widget.setCurrentRow(new_index)
            self.on_play_clicked()
        except Exception as e:
            QMessageBox.critical(self.ui, msg.TTL_ERR, f"{msg.MSG_NAV_ERR} {e}")

    def on_loop_clicked(self):
        """
        Handle loop button click.

        Toggles loop mode and updates navigation strategy accordingly.

        Raises:
            QMessageBox.critical: If there's an error toggling loop mode
        """
        try:
            self.music_controller.is_looped = not self.music_controller.is_looped
            self.ui.shuffle_songs_btn.setEnabled(not self.music_controller.is_looped)
            if self.music_controller.is_looped:
                self.navigation_handler.set_strategy(LoopingNavigationStrategy())
            else:
                self.navigation_handler.set_strategy(NormalNavigationStrategy())
        except Exception as e:
            QMessageBox.critical(self, msg.TTL_ERR, f"{msg.MSG_LOOP_ERR} {e}")

    def on_shuffle_clicked(self):
        """
        Handle shuffle button click.

        Toggles shuffle mode and updates navigation strategy accordingly.

        Raises:
            QMessageBox.critical: If there's an error toggling shuffle mode
        """
        try:
            self.music_controller.is_shuffled = not self.music_controller.is_shuffled
            self.ui.loop_one_btn.setEnabled(not self.music_controller.is_shuffled)
            if self.music_controller.is_shuffled:
                self.navigation_handler.set_strategy(RandomNavigationStrategy())
            else:
                self.navigation_handler.set_strategy(NormalNavigationStrategy())
        except Exception as e:
            QMessageBox.critical(self.ui, msg.TTL_ERR, f"{msg.MSG_SHFL_ERR} {e}")

    def handle_media_status(self, status):
        """
        Handle media status changes from the media player.

        Automatically plays the next song when current song reaches its end.

        Args:
            status: Current status of the media player (QMediaPlayer.MediaStatus)
        """
        if status == QMediaPlayer.EndOfMedia:
            self.on_next_previous_clicked()

    def on_volume_clicked(self, value):
        """
        Handle volume dial value changes.

        Updates both the music player volume and the volume display label.

        Args:
            value: New volume value (integer between 0 and 100)

        Raises:
            QMessageBox.critical: If there's an error setting the volume
        """
        try:
            self.music_controller.set_volume(value)
            self.ui.volume_label.setText(str(value))
        except Exception as e:
            QMessageBox.critical(self.ui, msg.TTL_ERR, f"{msg.MSG_VOL_ERR} {e}")

import os
from random import randint
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


class PlaybackHandler:
    """
    Обрабатывает действия воспроизведения: play, pause, stop.
    """

    def __init__(self, music_controller, ui_updater):
        """
        :param music_controller: Объект, реализующий IMusicPlayerController.
        :param ui_updater: Объект, обновляющий UI (например, UIUpdater).
        """
        self.music_controller = music_controller
        self.ui_updater = ui_updater

    def play(self, song_path: str) -> None:
        """Запускает воспроизведение песни и обновляет UI."""
        self.music_controller.play_song(song_path)
        self.ui_updater.update_current_song_info(song_path)

    def pause(self) -> None:
        """Приостанавливает или возобновляет воспроизведение в зависимости от состояния."""
        if self.music_controller.is_playing():
            self.music_controller.pause_song()
        elif self.music_controller.is_paused():
            self.music_controller.resume_song()

    def stop(self) -> None:
        """Останавливает воспроизведение и сбрасывает информацию в UI."""
        self.music_controller.stop_song()
        self.ui_updater.clear_song_info()


class NavigationHandler:
    """
    Обрабатывает навигацию по списку песен (next, previous) с использованием паттерна "Стратегия".
    """

    def __init__(self, navigation_strategy: INavigationStrategy = None):
        self.navigation_strategy = navigation_strategy or NormalNavigationStrategy()

    def set_strategy(self, strategy: INavigationStrategy) -> None:
        """
        Устанавливает новую стратегию навигации.

        :param strategy: Новая стратегия, реализующая INavigationStrategy.
        """
        self.navigation_strategy = strategy

    def get_next_index(self, current_index: int, count: int) -> int:
        return self.navigation_strategy.get_next_index(current_index, count)

    def get_previous_index(self, current_index: int, count: int) -> int:
        return self.navigation_strategy.get_previous_index(current_index, count)


class EventHandler:
    """
    Основной обработчик событий, агрегирующий специализированные обработчики.
    Делегирует действия по воспроизведению, навигации и обновлению UI соответствующим классам.
    """
    def __init__(
        self, ui, music_controller, playlist_manager, favourites_manager, ui_updater, db_manager
    ):
        self.ui = ui
        self.music_controller = music_controller
        self.playlist_manager = playlist_manager
        self.favourites_manager = favourites_manager
        self.ui_updater = ui_updater
        self.db_manager = db_manager
        self.playback_handler = PlaybackHandler(music_controller, ui_updater)
        self.navigation_handler = (NavigationHandler())

        self.setup_button_signals()

    def setup_button_signals(self):
        # Кнопки на вкладке Song List
        self.ui.add_songs_btn.clicked.connect(self.on_add_songs_clicked)
        self.ui.delete_selected_btn.clicked.connect(lambda: self.on_delete_selected_song_clicked(db_table=None))
        self.ui.delete_all_songs_btn.clicked.connect(lambda: self.on_clear_list_clicked(db_table=None))
        # Кнопки на вкладке Favourites
        self.ui.delete_selected_favourite_btn.clicked.connect(self.favourites_manager.remove_selected_favourite)
        self.ui.delete_all_favourites_btn.clicked.connect(self.favourites_manager.clear_favourites)
        # Кнопки на вкладке Playlist
        self.ui.new_playlist_btn.clicked.connect(lambda: self.playlist_manager.create_playlist(self.ui))
        self.ui.remove_selected_playlist_btn.clicked.connect(lambda: self.playlist_manager.remove_playlist(self.ui))
        self.ui.remove_all_playlists_btn.clicked.connect(lambda: self.playlist_manager.remove_all_playlists(self.ui))
        self.ui.load_selected_playlist_btn.clicked.connect(lambda: self.playlist_manager.load_playlist_into_widget(self.ui))
        # Кнопки добавления песен в списки
        self.ui.add_to_fav_btn.clicked.connect(lambda: self.favourites_manager.add_to_favourites())
        self.ui.add_to_playlist_btn.clicked.connect(lambda: self.playlist_manager.add_song_to_playlist(self.ui))

        # Управление воспроизведением
        self.ui.play_btn.clicked.connect(self.on_play_clicked)
        self.ui.pause_btn.clicked.connect(self.on_pause_clicked)
        self.ui.stop_btn.clicked.connect(self.on_stop_clicked)
        self.ui.next_btn.clicked.connect(lambda: self.on_next_previous_clicked(direction = "forward"))
        self.ui.previous_btn.clicked.connect(lambda: self.on_next_previous_clicked(direction = "buckward"))
        self.ui.loop_one_btn.clicked.connect(self.on_loop_clicked)
        self.ui.shuffle_songs_btn.clicked.connect(self.on_shuffle_clicked)
        self.ui.volume_dial.valueChanged.connect(self.on_volume_clicked)

        # Сигналы управления двойными кликами по спискам песен, плейлистов
        self.ui.loaded_songs_listWidget.itemDoubleClicked.connect(self.on_play_clicked)
        self.ui.favourites_listWidget.itemDoubleClicked.connect(self.on_play_clicked)
        self.ui.playlists_listWidget.itemDoubleClicked.connect(lambda: self.playlist_manager.load_playlist_into_widget(self.ui))

        # Служебные сигналы
        self.music_controller.media_player().mediaStatusChanged.connect(self.handle_media_status)

    def get_current_list_widget(self):
        # Выбираем виджет списка в зависимости от активной вкладки
        idx = self.ui.stackedWidget.currentIndex()
        if idx == 0:
            return self.ui.loaded_songs_listWidget
        elif idx == 1:
            return self.ui.playlists_listWidget
        elif idx == 2:
            return self.ui.favourites_listWidget
        return None

    def on_add_songs_clicked(self):
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
        try:
            list_widget = self.get_current_list_widget()
            if list_widget is None or list_widget.count() == 0:
                QMessageBox.information(self.ui, msg.TTL_ATT, msg.MSG_NO_SONG_TO_DEL)
                return
            item = list_widget.currentItem()
            if not item:
                QMessageBox.information(self.ui, msg.TTL_ATT, msg.MSG_NO_SONG_SEL)
                return
            
            current_song = item.data(Qt.UserRole)

            # Проверяем, не играет ли сейчас эта песня
            current_media = self.music_controller.media_player().media()
            current_song_url = current_media.canonicalUrl().toLocalFile()
            was_playing = (self.music_controller.media_player().state()== QMediaPlayer.PlayingState)
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

    def on_clear_list_clicked(self,db_table=None):
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
            QMessageBox.critical(self.ui, msg.TTL_ERR, f"{msg.MSG_ALL_SONG_DEL_ERR} {e}")

    def on_play_clicked(self):
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
        self.playback_handler.pause()

    def on_stop_clicked(self):
        self.playback_handler.stop()

    def on_next_previous_clicked(self, direction: str = "forward"):
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
                new_index = self.navigation_handler.get_previous_index(current_index, count)
            else:
                new_index = current_index

            list_widget.setCurrentRow(new_index)
            self.on_play_clicked()
        except Exception as e:
            QMessageBox.critical(self.ui, msg.TTL_ERR, f"{msg.MSG_NAV_ERR} {e}")

    def on_loop_clicked(self):
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
        if status == QMediaPlayer.EndOfMedia:
            self.on_next_previous_clicked()

    def on_volume_clicked(self, value):
        try:
            self.music_controller.set_volume(value)
            self.ui.volume_label.setText(str(value))
        except Exception as e:
            QMessageBox.critical(self.ui, msg.TTL_ERR, f"{msg.MSG_VOL_ERR} {e}")

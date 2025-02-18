import os
import sys
from typing import Optional

from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox


from music import Ui_MusicApp
from database.db_manager import DatabaseManager
from interfaces.interfaces import IDatabaseManager, IMusicPlayerController
from interfaces.playlists.playlist_manager import PlaylistManager
from controllers.background_slideshow import BackgroundSlideshow
from controllers.music_player_controller import MusicPlayerController
from controllers.context_manager import ContextMenuManager
from controllers.favourites_manager import FavouritesManager
from controllers.window_manager import WindowManager
from controllers.ui_updater import UIUpdater, SongInfoLabels
from controllers.event_handler import EventHandler, EventHandlerConfig


class ModernMusicPlayer(QMainWindow, Ui_MusicApp):
    # pylint: disable=too-many-instance-attributes
    """
    Главное окно приложения Modern Music Player.
    Отвечает за инициализацию зависимостей, настройку интерфейса и обработку событий.
    """

    def __init__(
        self,
        db_manager: IDatabaseManager,
        music_controller: IMusicPlayerController,
        event_handler: Optional["EventHandler"] = None,
    ):
        """
        Инициализирует главное окно и его компоненты.

        :param db_manager: Менеджер базы данных, реализующий IDatabaseManager.
        :param music_controller: Контроллер музыки, реализующий IMusicPlayerController.
        """
        super().__init__()
        self.setupUi(self)

        # Инициализация WindowManager
        self.window_manager = WindowManager(self)
        self.window_manager.setup_window()

        # Переопределяем обработчики событий для окна
        self.title_frame.mouseMoveEvent = self.window_manager.handleMouseMoveEvent

        # Инициализация базы данных
        self.db_manager = db_manager
        self.db_manager.create_table("favourites")
        self.current_playlist: Optional[str] = None

        # Инициализация менеджера плейлистов
        self.playlist_manager = PlaylistManager(
            self.db_manager, self.playlists_listWidget
        )

        # Инициализация менеджера избранных песен
        self.favourites_manager = FavouritesManager(self)

        # Инициализация контроллера музыки
        self.music_controller = music_controller
        initial_volume = 15
        self.music_controller.set_volume(initial_volume)
        self.volume_dial.setValue(initial_volume)
        self.volume_label.setText(str(initial_volume))

        # Инициализация контроллера изменения UI
        song_info = SongInfoLabels(
            self.current_song_title,
            self.current_song_artist,
            self.current_song_album,
            self.current_song_duration,
        )
        self.ui_updater = UIUpdater(
            music_controller=self.music_controller,
            slider=self.music_slider,
            time_label=self.time_label,
            song_info=song_info,
        )
        self.is_slider_moving = False

        # Инициализация EventHandler для обработки нажатий кнопок и действий контекстного меню
        self.event_handler = event_handler

        # Менеджер контекстного меню и передаём ему self
        self.context_menu_manager = ContextMenuManager(
            self,
            self.event_handler,
            self.favourites_manager,
            self.playlist_manager,
        )

        # Запуск BackgroundSlideshow
        images_dir = os.path.join(os.getcwd(), "utils", "bg_imgs")
        self.slideshow = BackgroundSlideshow(
            label=self.background_image, images_dir=images_dir, interval_ms=120000
        )
        self.slideshow.start()

        # -------------------- Сигналы и слоты -------------------

        # Служебные сигналы
        self.music_slider.sliderPressed.connect(self.slider_pressed)
        self.music_slider.sliderReleased.connect(self.slider_released)

        # Переключение вкладок
        self.song_list_btn.clicked.connect(self.switch_to_songs_tab)
        self.playlists_btn.clicked.connect(self.switch_to_playlists_tab)
        self.favourites_btn.clicked.connect(self.switch_to_favourites_tab)

        # Изначально переходим на вкладку 0
        self.switch_to_songs_tab()

        # Подключаем кнопку about к методу, который покажет окно с информацией
        self.about_btn.clicked.connect(self.show_about)

    # -------------------- Базовые методы ---------------------

    def mousePressEvent(self, event):
        """Обрабатывает событие нажатия мыши."""
        self.window_manager.handleMousePressEvent(event)

    def slider_pressed(self):
        """Вызывается при начале движения слайдера."""
        self.is_slider_moving = True

    def slider_released(self):
        """Вызывается при отпускании слайдера и устанавливает новую позицию."""
        self.is_slider_moving = False
        new_position = self.music_slider.value()
        self.music_controller.media_player().setPosition(new_position)

    def show_about(self):
        """Отображает окно «О программе» с информацией о проекте."""
        about_text = """
        <h2>Modern Music Player</h2>
        <p>Version: 1.3</p>
        <p>Author: Oleksandr Kharchenko</p>
        <p>Email: oleksandr.kharchenko@icloud.com</p>
        <p>Description: Application for the listening music.</p>
        """
        QMessageBox.about(self, "О программе", about_text)

    # ---------------- Переключение вкладок -------------------

    def switch_to_songs_tab(self):
        """Переключает вкладку на список песен."""
        self.stackedWidget.setCurrentIndex(0)

    def switch_to_playlists_tab(self):
        """Переключает вкладку на плейлисты и загружает их."""
        self.stackedWidget.setCurrentIndex(1)
        self.playlist_manager.load_playlists_into_widget()

    def switch_to_favourites_tab(self):
        """Переключает вкладку на избранное и загружает его."""
        self.stackedWidget.setCurrentIndex(2)
        self.favourites_manager.load_favourites()


class AppFactory:
    """
    Фабрика для создания и связывания (настраивания) всех зависимостей приложения.
    """

    @staticmethod
    def create_app() -> ModernMusicPlayer:
        """
        Фабрика по созданию приложения.
        """
        db_manager = DatabaseManager()
        music_controller = MusicPlayerController()
        new_player = ModernMusicPlayer(db_manager, music_controller, event_handler=None)
        # Создаем конфигурацию для EventHandler
        config = EventHandlerConfig(
            ui=new_player,
            music_controller=music_controller,
            playlist_manager=new_player.playlist_manager,
            favourites_manager=new_player.favourites_manager,
            ui_updater=new_player.ui_updater,
            db_manager=db_manager,
        )
        event_handler = EventHandler(config)
        # Инициализируем обработчик событий с этой конфигурацией
        new_player.event_handler = event_handler
        return new_player


def set_working_directory():
    """
    Устанавливает рабочую директорию в каталог приложения.
    """
    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_path)


if __name__ == "__main__":
    # Устанавливаем рабочую директорию в каталог приложения
    set_working_directory()

    app = QApplication(sys.argv)
    player = AppFactory.create_app()
    player.show()
    sys.exit(app.exec_())

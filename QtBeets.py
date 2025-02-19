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
    Main window of the Modern Music Player application.

    Responsible for initializing dependencies, setting up the interface,
    and handling events. This class serves as the central component that
    coordinates all player functionality.
    """

    def __init__(
        self,
        db_manager: IDatabaseManager,
        music_controller: IMusicPlayerController,
        event_handler: Optional["EventHandler"] = None,
    ):
        """
        Initialize the main window and its components.

        Args:
            db_manager (IDatabaseManager): Database manager that implements IDatabaseManager interface.
            music_controller (IMusicPlayerController): Music controller that implements IMusicPlayerController interface.
            event_handler (Optional[EventHandler]): Event handler for processing button clicks and context menu actions.
        """
        super().__init__()
        self.setupUi(self)

        # Initialize WindowManager
        self.window_manager = WindowManager(self)
        self.window_manager.setup_window()

        # Override event handlers for window
        self.title_frame.mouseMoveEvent = self.window_manager.handleMouseMoveEvent

        # Initialize database
        self.db_manager = db_manager
        self.db_manager.create_table("favourites")
        self.current_playlist: Optional[str] = None

        # Initialize playlist manager
        self.playlist_manager = PlaylistManager(
            self.db_manager, self.playlists_listWidget
        )

        # Initialize favorites manager
        self.favourites_manager = FavouritesManager(self)

        # Initialize music controller
        self.music_controller = music_controller
        initial_volume = 15
        self.music_controller.set_volume(initial_volume)
        self.volume_dial.setValue(initial_volume)
        self.volume_label.setText(str(initial_volume))

        # Initialize UI updater controller
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

        # Initialize EventHandler for handling button clicks and context menu actions
        self.event_handler = event_handler

        # Context menu manager, passing self
        self.context_menu_manager = ContextMenuManager(
            self,
            self.event_handler,
            self.favourites_manager,
            self.playlist_manager,
        )

        # Start BackgroundSlideshow
        images_dir = os.path.join(os.getcwd(), "utils", "bg_imgs")
        self.slideshow = BackgroundSlideshow(
            label=self.background_image, images_dir=images_dir, interval_ms=120000
        )
        self.slideshow.start()

        # -------------------- Signals and slots -------------------

        # Service signals
        self.music_slider.sliderPressed.connect(self.slider_pressed)
        self.music_slider.sliderReleased.connect(self.slider_released)

        # Tab switching
        self.song_list_btn.clicked.connect(self.switch_to_songs_tab)
        self.playlists_btn.clicked.connect(self.switch_to_playlists_tab)
        self.favourites_btn.clicked.connect(self.switch_to_favourites_tab)

        # Initially switch to tab 0
        self.switch_to_songs_tab()

        # Connect about button to method that shows information window
        self.about_btn.clicked.connect(self.show_about)

    # -------------------- Basic methods ---------------------

    def mousePressEvent(self, event):
        """
        Handle mouse press event.

        Args:
            event: The mouse press event to be handled.
        """
        self.window_manager.handleMousePressEvent(event)

    def slider_pressed(self):
        """
        Called when the slider movement begins.

        Sets the internal flag to indicate that the slider is currently being moved by the user.
        """
        self.is_slider_moving = True

    def slider_released(self):
        """
        Called when the slider is released and sets the new position.

        Updates the music player's position based on the slider's current value
        and resets the movement flag.
        """
        self.is_slider_moving = False
        new_position = self.music_slider.value()
        self.music_controller.media_player().setPosition(new_position)

    def show_about(self):
        """
        Display the "About" window with project information.

        Shows a message box containing information about the application,
        including version, author, and brief description.
        """
        about_text = """
        <h2>Modern Music Player</h2>
        <p>Version: 1.3</p>
        <p>Author: Oleksandr Kharchenko</p>
        <p>Email: oleksandr.kharchenko@icloud.com</p>
        <p>Description: Application for the listening music.</p>
        """
        QMessageBox.about(self, "О программе", about_text)

    # ---------------- Tab switching -------------------

    def switch_to_songs_tab(self):
        """
        Switch to the songs list tab.

        Changes the current index of the stacked widget to display the songs list.
        """
        self.stackedWidget.setCurrentIndex(0)

    def switch_to_playlists_tab(self):
        """
        Switch to the playlists tab and load playlists.

        Changes the current index of the stacked widget to display playlists
        and triggers loading of available playlists into the list widget.
        """
        self.stackedWidget.setCurrentIndex(1)
        self.playlist_manager.load_playlists_into_widget()

    def switch_to_favourites_tab(self):
        """
        Switch to the favorites tab and load favorites.

        Changes the current index of the stacked widget to display favorites
        and triggers loading of saved favorite songs.
        """
        self.stackedWidget.setCurrentIndex(2)
        self.favourites_manager.load_favourites()


class AppFactory:
    """
    Factory for creating and connecting (configuring) all application dependencies.

    Provides methods to create a fully configured Modern Music Player application
    with all required components properly connected.
    """

    @staticmethod
    def create_app() -> ModernMusicPlayer:
        """
        Factory method for creating the application.

        Creates all necessary components (database manager, music controller, etc.),
        connects them together, and returns a fully initialized ModernMusicPlayer instance.

        Returns:
            ModernMusicPlayer: A fully initialized application instance ready to be shown.
        """
        db_manager = DatabaseManager()
        music_controller = MusicPlayerController()
        new_player = ModernMusicPlayer(db_manager, music_controller, event_handler=None)
        # Create configuration for EventHandler
        config = EventHandlerConfig(
            ui=new_player,
            music_controller=music_controller,
            playlist_manager=new_player.playlist_manager,
            favourites_manager=new_player.favourites_manager,
            ui_updater=new_player.ui_updater,
            db_manager=db_manager,
        )
        event_handler = EventHandler(config)
        # Initialize event handler with this configuration
        new_player.event_handler = event_handler
        return new_player


def set_working_directory():
    """
    Set the working directory to the application directory.

    Determines whether the application is running from a frozen executable or as a script,
    and sets the current working directory appropriately to ensure proper resource loading.
    """
    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_path)


if __name__ == "__main__":
    # Set working directory to application directory
    set_working_directory()

    app = QApplication(sys.argv)
    player = AppFactory.create_app()
    player.show()
    sys.exit(app.exec_())

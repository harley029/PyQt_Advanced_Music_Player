# pylint: disable=redefined-outer-name
from unittest.mock import Mock, MagicMock, patch
import pytest

from QtBeets import ModernMusicPlayer, AppFactory, set_working_directory
from utils.messages import about_message


@pytest.fixture
def ui_mocks():
    """
    Create and return a dictionary of mock UI elements.

    This fixture provides mock objects for all UI elements used in the ModernMusicPlayer
    to facilitate testing without requiring the actual UI implementation.

    Returns:
        dict: A dictionary mapping UI element names to their corresponding mock objects.
    """
    return {
        "stackedWidget": MagicMock(),
        "music_slider": MagicMock(),
        "time_label": MagicMock(),
        "current_song_title": MagicMock(),
        "current_song_artist": MagicMock(),
        "current_song_album": MagicMock(),
        "current_song_duration": MagicMock(),
        "volume_dial": MagicMock(),
        "volume_label": MagicMock(),
        "title_frame": MagicMock(),
        "background_image": MagicMock(),
        "song_list_btn": MagicMock(),
        "playlists_btn": MagicMock(),
        "favourites_btn": MagicMock(),
        "about_btn": MagicMock(),
        "playlists_listWidget": MagicMock(),
    }


class MockUiMusicApp:
    """
    Mock implementation of the Ui_MusicApp class from the PyQt UI file.

    This class provides a simplified version of the setupUi method that creates
    mock objects for all the UI elements instead of building the actual UI,
    allowing for tests to run without the actual UI implementation.
    """

    def setupUi(self, window):
        """
        Set up mock UI elements on the provided window object.

        This method mimics the behavior of the auto-generated setupUi method from
        PyQt UI files by creating mock objects for all UI elements and attaching
        them to the provided window.

        Args:
            window: The window object to which the mock UI elements will be attached.
        """
        window.stackedWidget = MagicMock()
        window.music_slider = MagicMock()
        window.time_label = MagicMock()
        window.current_song_title = MagicMock()
        window.current_song_artist = MagicMock()
        window.current_song_album = MagicMock()
        window.current_song_duration = MagicMock()
        window.volume_dial = MagicMock()
        window.volume_label = MagicMock()
        window.title_frame = MagicMock()
        window.background_image = MagicMock()
        window.song_list_btn = MagicMock()
        window.playlists_btn = MagicMock()
        window.favourites_btn = MagicMock()
        window.about_btn = MagicMock()
        window.playlists_listWidget = MagicMock()


@pytest.fixture
def mock_dependencies():
    """
    Fixture to provide mocked dependencies for the ModernMusicPlayer.

    Creates and configures mock objects for the database manager, music controller,
    event handler, and context menu manager with predefined return values to
    simulate their behavior during tests.

    Returns:
        tuple: A tuple containing mock objects for (db_manager, music_controller,
               event_handler, context_menu_manager).
    """
    db_manager = Mock()
    db_manager.get_tables.return_value = ["playlist1", "playlist2", "favourites"]
    db_manager.fetch_all_songs.return_value = ["song1.mp3", "song2.mp3"]
    music_controller = Mock()
    music_controller.media_player.return_value = Mock()
    event_handler = Mock()
    context_menu_manager = Mock()
    return db_manager, music_controller, event_handler, context_menu_manager


@pytest.fixture
def music_player(mock_dependencies):
    """
    Fixture to create a ModernMusicPlayer instance with mocked dependencies.

    This fixture creates a fully mocked ModernMusicPlayer instance by:
    1. Using the mock_dependencies fixture to get core dependencies
    2. Patching various classes used by ModernMusicPlayer
    3. Creating a player instance and manually setting up its mocked attributes

    Args:
        mock_dependencies: The fixture providing the mocked dependencies.

    Returns:
        ModernMusicPlayer: A configured instance with all dependencies mocked.
    """
    db_manager, music_controller, event_handler, context_menu_manager = (
        mock_dependencies
    )
    with patch("QtBeets.Ui_MusicApp", MockUiMusicApp), patch(
        "QtBeets.WindowManager", return_value=Mock()
    ) as mock_wm, patch(
        "QtBeets.BackgroundSlideshow", return_value=Mock()
    ) as mock_slideshow, patch(
        "QtBeets.PlaylistManager", return_value=Mock()
    ) as mock_pm, patch(
        "QtBeets.FavouritesManager", return_value=Mock()
    ) as mock_fm:
        player = ModernMusicPlayer(
            db_manager, music_controller, event_handler, context_menu_manager
        )
        player.window_manager = mock_wm.return_value
        player.slideshow = mock_slideshow.return_value
        player.playlist_manager = mock_pm.return_value
        player.favourites_manager = mock_fm.return_value
        player.stackedWidget = MagicMock()
        player.music_slider = MagicMock()
        player.time_label = MagicMock()
        player.current_song_title = MagicMock()
        player.current_song_artist = MagicMock()
        player.current_song_album = MagicMock()
        player.current_song_duration = MagicMock()
        player.volume_dial = MagicMock()
        player.volume_label = MagicMock()
        player.title_frame = MagicMock()
        player.background_image = MagicMock()
        player.song_list_btn = MagicMock()
        player.playlists_btn = MagicMock()
        player.favourites_btn = MagicMock()
        player.about_btn = MagicMock()
        player.playlists_listWidget = MagicMock()
    return player


def test_init(music_player, mock_dependencies):
    """
    Test initialization of ModernMusicPlayer.

    Verifies that:
    1. All dependencies are correctly assigned to instance attributes
    2. The 'favourites' table is created in the database
    3. The background slideshow is started

    Args:
        music_player: The fixture providing a mocked ModernMusicPlayer instance.
        mock_dependencies: The fixture providing the mocked dependencies.
    """
    db_manager, music_controller, event_handler, context_menu_manager = (
        mock_dependencies
    )
    assert music_player.db_manager == db_manager
    assert music_player.music_controller == music_controller
    assert music_player.event_handler == event_handler
    assert music_player.context_menu_manager == context_menu_manager
    db_manager.create_table.assert_called_once_with("favourites")
    music_player.slideshow.start.assert_called_once()


def test_mouse_press_event(music_player):
    """
    Test that mousePressEvent delegates to WindowManager.

    Verifies that when a mouse press event occurs, the event is correctly
    delegated to the window_manager's handleMousePressEvent method.

    Args:
        music_player: The fixture providing a mocked ModernMusicPlayer instance.
    """
    event = Mock()
    music_player.mousePressEvent(event)
    music_player.window_manager.handleMousePressEvent.assert_called_once_with(event)


def test_slider_pressed(music_player):
    """
    Test that slider_pressed sets the is_slider_moving flag.

    Verifies that when the slider is pressed, the is_slider_moving flag
    is set to True to indicate that the slider is being manipulated by the user.

    Args:
        music_player: The fixture providing a mocked ModernMusicPlayer instance.
    """
    assert music_player.is_slider_moving is False
    music_player.slider_pressed()
    assert music_player.is_slider_moving is True


def test_slider_released(music_player):
    """
    Test that slider_released updates position and resets flag.

    Verifies that when the slider is released:
    1. The media player's position is updated to the slider's current value
    2. The is_slider_moving flag is reset to False

    Args:
        music_player: The fixture providing a mocked ModernMusicPlayer instance.
    """
    music_player.is_slider_moving = True
    music_player.music_slider.value.return_value = 5000
    music_player.slider_released()
    assert music_player.is_slider_moving is False
    music_player.music_controller.media_player().setPosition.assert_called_once_with(
        5000
    )


def test_show_about(music_player):
    """
    Test that show_about displays the about message box.

    Verifies that when the about button is clicked, a message box is displayed
    with the correct title and content from the about_message.

    Args:
        music_player: The fixture providing a mocked ModernMusicPlayer instance.
    """
    with patch("PyQt5.QtWidgets.QMessageBox.about") as mock_msgbox:
        music_player.show_about()
        mock_msgbox.assert_called_once_with(music_player, "О программе", about_message)


def test_switch_to_songs_tab(music_player):
    """
    Test that switch_to_songs_tab sets stacked widget index to 0.

    Verifies that when switching to the songs tab, the stacked widget's
    current index is set to 0 to display the songs view.

    Args:
        music_player: The fixture providing a mocked ModernMusicPlayer instance.
    """
    music_player.switch_to_songs_tab()
    music_player.stackedWidget.setCurrentIndex.assert_called_once_with(0)


def test_switch_to_playlists_tab(music_player):
    """
    Test that switch_to_playlists_tab sets index and loads playlists.

    Verifies that when switching to the playlists tab:
    1. The stacked widget's current index is set to 1
    2. The playlist manager's load_playlists_into_widget method is called

    Args:
        music_player: The fixture providing a mocked ModernMusicPlayer instance.
    """
    music_player.switch_to_playlists_tab()
    music_player.stackedWidget.setCurrentIndex.assert_called_once_with(1)
    music_player.playlist_manager.load_playlists_into_widget.assert_called_once()


def test_switch_to_favourites_tab(music_player):
    """
    Test that switch_to_favourites_tab sets index and loads favourites.

    Verifies that when switching to the favourites tab:
    1. The stacked widget's current index is set to 2
    2. The favourites manager's load_favourites method is called

    Args:
        music_player: The fixture providing a mocked ModernMusicPlayer instance.
    """
    music_player.switch_to_favourites_tab()
    music_player.stackedWidget.setCurrentIndex.assert_called_once_with(2)
    music_player.favourites_manager.load_favourites.assert_called_once()


def test_app_factory_create_app():
    """
    Test that AppFactory creates a fully configured ModernMusicPlayer.

    Verifies that the AppFactory.create_app method:
    1. Creates all required dependencies (DatabaseManager, MusicPlayerController, etc.)
    2. Returns a properly instantiated ModernMusicPlayer
    """
    with patch("QtBeets.DatabaseManager", return_value=Mock()) as mock_db, patch(
        "QtBeets.MusicPlayerController", return_value=Mock()
    ) as mock_mc, patch("QtBeets.EventHandler") as mock_eh, patch(
        "QtBeets.ContextMenuManager"
    ) as mock_cm:
        player = AppFactory.create_app()
        mock_db.assert_called_once()
        mock_mc.assert_called_once()
        assert mock_eh.called
        assert mock_cm.called
        assert isinstance(player, ModernMusicPlayer)


def test_set_working_directory_frozen():
    """
    Test set_working_directory when running as frozen executable.

    Verifies that when running as a frozen executable (e.g., PyInstaller):
    1. The function correctly detects the frozen state
    2. Changes the current working directory to the executable's directory
    """
    with patch("sys.frozen", True, create=True), patch(
        "os.path.dirname", return_value="/fake/executable/path"
    ), patch("os.chdir") as mock_chdir:
        set_working_directory()
        mock_chdir.assert_called_once_with("/fake/executable/path")


def test_set_working_directory_script():
    """
    Test set_working_directory when running as script.

    Verifies that when running as a regular Python script:
    1. The function correctly detects the non-frozen state
    2. Changes the current working directory to the script's directory
    """
    with patch("sys.frozen", False, create=True), patch(
        "os.path.abspath", return_value="/fake/script/path/file.py"
    ), patch("os.path.dirname", return_value="/fake/script/path"), patch(
        "os.chdir"
    ) as mock_chdir:
        set_working_directory()
        mock_chdir.assert_called_once_with("/fake/script/path")

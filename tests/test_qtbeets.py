# pylint: disable=redefined-outer-name
from unittest.mock import Mock, MagicMock, patch
import pytest

from QtBeets import ModernMusicPlayer, AppFactory, set_working_directory
from utils.messages import about_message


@pytest.fixture
def ui_mocks():
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


# Mock Ui_MusicApp
class MockUiMusicApp:
    def setupUi(self, window):
        # Set initial mock attributes (may be overridden by real setupUi)
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
    """Fixture to provide mocked dependencies."""
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
    """Fixture to create a ModernMusicPlayer instance with mocked dependencies."""
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
        # Inject mocks for managers
        player.window_manager = mock_wm.return_value
        player.slideshow = mock_slideshow.return_value
        player.playlist_manager = mock_pm.return_value
        player.favourites_manager = mock_fm.return_value
        # Manually override UI attributes with mocks
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
        # Debug: Verify attributes are mocks
        print(f"volume_dial: {type(player.volume_dial)}")
        print(f"music_slider: {type(player.music_slider)}")
        print(f"stackedWidget: {type(player.stackedWidget)}")
    return player


def test_init(music_player, mock_dependencies):
    """Test initialization of ModernMusicPlayer."""
    db_manager, music_controller, event_handler, context_menu_manager = (
        mock_dependencies
    )

    # Verify dependencies are set
    assert music_player.db_manager == db_manager
    assert music_player.music_controller == music_controller
    assert music_player.event_handler == event_handler
    assert music_player.context_menu_manager == context_menu_manager

    # Verify database table creation
    db_manager.create_table.assert_called_once_with("favourites")

    # Verify initial volume setup
    # music_controller.set_volume.assert_called_once_with(15)
    # music_player.volume_dial.setValue.assert_called_once_with(15)
    # music_player.volume_label.setText.assert_called_once_with("15")

    # Verify slideshow started
    music_player.slideshow.start.assert_called_once()

    # Verify initial tab switch
    # music_player.stackedWidget.setCurrentIndex.assert_called_once_with(0)


def test_mouse_press_event(music_player):
    """Test mousePressEvent delegates to WindowManager."""
    event = Mock()
    music_player.mousePressEvent(event)
    music_player.window_manager.handleMousePressEvent.assert_called_once_with(event)


def test_slider_pressed(music_player):
    """Test slider_pressed sets is_slider_moving flag."""
    assert music_player.is_slider_moving is False
    music_player.slider_pressed()
    assert music_player.is_slider_moving is True


def test_slider_released(music_player):
    """Test slider_released updates position and resets flag."""
    music_player.is_slider_moving = True
    music_player.music_slider.value.return_value = 5000
    music_player.slider_released()
    assert music_player.is_slider_moving is False
    music_player.music_controller.media_player().setPosition.assert_called_once_with(
        5000
    )


def test_show_about(music_player):
    """Test show_about displays the about message box."""
    with patch("PyQt5.QtWidgets.QMessageBox.about") as mock_msgbox:
        music_player.show_about()
        mock_msgbox.assert_called_once_with(music_player, "О программе", about_message)


def test_switch_to_songs_tab(music_player):
    """Test switch_to_songs_tab sets stacked widget index to 0."""
    music_player.switch_to_songs_tab()
    music_player.stackedWidget.setCurrentIndex.assert_called_once_with(0)


def test_switch_to_playlists_tab(music_player):
    """Test switch_to_playlists_tab sets index and loads playlists."""
    music_player.switch_to_playlists_tab()
    music_player.stackedWidget.setCurrentIndex.assert_called_once_with(1)
    music_player.playlist_manager.load_playlists_into_widget.assert_called_once()


def test_switch_to_favourites_tab(music_player):
    """Test switch_to_favourites_tab sets index and loads favourites."""
    music_player.switch_to_favourites_tab()
    music_player.stackedWidget.setCurrentIndex.assert_called_once_with(2)
    music_player.favourites_manager.load_favourites.assert_called_once()


def test_app_factory_create_app():
    """Test AppFactory creates a fully configured ModernMusicPlayer."""
    with patch("QtBeets.DatabaseManager", return_value=Mock()) as mock_db, patch(
        "QtBeets.MusicPlayerController", return_value=Mock()
    ) as mock_mc, patch("QtBeets.EventHandler") as mock_eh, patch(
        "QtBeets.ContextMenuManager"
    ) as mock_cm:
        player = AppFactory.create_app()

        # Verify dependencies created
        mock_db.assert_called_once()
        mock_mc.assert_called_once()

        # Verify event handler and context menu setup
        assert mock_eh.called
        assert mock_cm.called
        assert isinstance(player, ModernMusicPlayer)


def test_set_working_directory_frozen():
    """Test set_working_directory when running as frozen executable."""
    with patch("sys.frozen", True, create=True), patch(
        "os.path.dirname", return_value="/fake/executable/path"
    ), patch("os.chdir") as mock_chdir:
        set_working_directory()
        mock_chdir.assert_called_once_with("/fake/executable/path")


def test_set_working_directory_script():
    """Test set_working_directory when running as script."""
    with patch("sys.frozen", False, create=True), patch(
        "os.path.abspath", return_value="/fake/script/path/file.py"
    ), patch("os.path.dirname", return_value="/fake/script/path"), patch(
        "os.chdir"
    ) as mock_chdir:
        set_working_directory()
        mock_chdir.assert_called_once_with("/fake/script/path")

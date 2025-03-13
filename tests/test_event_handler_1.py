# pylint: disable=redefined-outer-name
from sqlite3 import OperationalError

from unittest.mock import MagicMock, patch
import pytest

from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QFileDialog, QMessageBox
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtCore import Qt

from controllers.event_handler import (
    EventHandler,
    EventHandlerConfig,
    UIComponents,
    MediaComponents,
    StorageComponents,
    PlaybackHandler,
    NavigationHandler,
    UIEventHandler,
)
from interfaces.navigation.navigation import (
    NormalNavigationStrategy,
    RandomNavigationStrategy,
    LoopingNavigationStrategy,
)
from utils import messages as msg
from utils.list_manager import ListManager


@pytest.fixture
def mock_ui():
    """
    Create a mock UI object with necessary widgets and attributes for testing.

    This fixture provides a mock UI object that simulates the expected interface
    of the application's main UI, including all relevant widgets and their
    expected behaviors.

    Returns:
        MagicMock: A mock object representing the application's main UI with all
                   necessary widgets and attributes properly configured.
    """
    ui = MagicMock()
    ui.loaded_songs_listWidget = MagicMock(spec=QListWidget)
    ui.favourites_listWidget = MagicMock(spec=QListWidget)
    ui.playlists_listWidget = MagicMock(spec=QListWidget)
    ui.current_playlist = None
    ui.ui_provider = MagicMock()
    ui.volume_label = MagicMock()
    ui.add_songs_btn = MagicMock()
    ui.delete_selected_btn = MagicMock()
    ui.delete_all_songs_btn = MagicMock()
    ui.delete_selected_favourite_btn = MagicMock()
    ui.delete_all_favourites_btn = MagicMock()
    ui.new_playlist_btn = MagicMock()
    ui.remove_selected_playlist_btn = MagicMock()
    ui.remove_all_playlists_btn = MagicMock()
    ui.load_selected_playlist_btn = MagicMock()
    ui.add_to_fav_btn = MagicMock()
    ui.add_to_playlist_btn = MagicMock()
    ui.play_btn = MagicMock()
    ui.pause_btn = MagicMock()
    ui.stop_btn = MagicMock()
    ui.next_btn = MagicMock()
    ui.previous_btn = MagicMock()
    ui.loop_one_btn = MagicMock()
    ui.shuffle_songs_btn = MagicMock()
    ui.volume_dial = MagicMock()
    return ui


@pytest.fixture
def mock_config(mock_ui):
    """
    Create a mock EventHandlerConfig with all required dependencies.

    This fixture sets up a complete configuration object with mock components
    for UI, media, and storage. It also patches the ListManager to return
    predictable results for testing.

    Args:
        mock_ui (MagicMock): The mock UI object created by the mock_ui fixture.

    Yields:
        EventHandlerConfig: A properly configured mock EventHandlerConfig object
                           with all dependencies injected.

    Notes:
        This fixture uses a context manager to patch the ListManager class,
        ensuring the patch is properly removed after the test completes.
    """
    ui_components = UIComponents(main_window=mock_ui, ui_updater=MagicMock())
    media_components = MediaComponents(
        music_controller=MagicMock(),
        playlist_manager=MagicMock(),
        favourites_manager=MagicMock(),
    )
    storage_components = StorageComponents(db_manager=MagicMock())
    config = EventHandlerConfig(ui_components, media_components, storage_components)
    mock_list_manager = MagicMock(spec=ListManager)
    mock_list_manager.get_current_widget.return_value = MagicMock(spec=QListWidget)
    mock_list_manager.get_selected_song.return_value = None
    patcher = patch(
        "controllers.event_handler.ListManager", return_value=mock_list_manager
    )
    patcher.start()
    yield config
    patcher.stop()


@pytest.fixture
def event_handler(mock_config):
    """
    Create an EventHandler instance for testing.

    This fixture instantiates an EventHandler using the provided mock configuration,
    making it ready for testing various event handling functionalities.

    Args:
        mock_config (EventHandlerConfig): The mock configuration created by the
                                         mock_config fixture.

    Returns:
        EventHandler: An instantiated EventHandler object configured with mock
                     dependencies.
    """
    return EventHandler(mock_config)


# --- PlaybackHandler Tests ---


def test_playback_handler_play():
    """
    Test that PlaybackHandler.play properly calls music_controller and ui_updater.

    This test verifies that when PlaybackHandler.play is called with a song path,
    it correctly delegates to the music_controller's play_song method and updates
    the UI via the ui_updater.

    Expected behavior:
        - music_controller.play_song should be called once with the song path
        - ui_updater.update_current_song_info should be called once with the song path
    """
    music_controller = MagicMock()
    ui_updater = MagicMock()
    handler = PlaybackHandler(music_controller, ui_updater)
    handler.play("/path/to/song.mp3")
    music_controller.play_song.assert_called_once_with("/path/to/song.mp3")
    ui_updater.update_current_song_info.assert_called_once_with("/path/to/song.mp3")


def test_playback_handler_pause_playing():
    """
    Test PlaybackHandler.pause when a song is currently playing.

    This test verifies that when a song is in playing state and pause is called,
    the music_controller correctly pauses the song and does not attempt to resume it.

    Expected behavior:
        - music_controller.pause_song should be called once
        - music_controller.resume_song should not be called
    """
    music_controller = MagicMock()
    ui_updater = MagicMock()
    music_controller.is_playing.return_value = True
    handler = PlaybackHandler(music_controller, ui_updater)
    handler.pause()
    music_controller.pause_song.assert_called_once()
    music_controller.resume_song.assert_not_called()


def test_playback_handler_pause_paused():
    """
    Test PlaybackHandler.pause when a song is currently paused.

    This test verifies that when a song is in paused state and pause is called,
    the music_controller correctly resumes the song and does not attempt to pause it again.

    Expected behavior:
        - music_controller.resume_song should be called once
        - music_controller.pause_song should not be called
    """
    music_controller = MagicMock()
    ui_updater = MagicMock()
    music_controller.is_playing.return_value = False
    music_controller.is_paused.return_value = True
    handler = PlaybackHandler(music_controller, ui_updater)
    handler.pause()
    music_controller.resume_song.assert_called_once()
    music_controller.pause_song.assert_not_called()


def test_playback_handler_stop():
    """
    Test PlaybackHandler.stop properly calls music_controller and ui_updater.

    This test verifies that when PlaybackHandler.stop is called, it correctly
    delegates to the music_controller's stop_song method and clears the UI info.

    Expected behavior:
        - music_controller.stop_song should be called once
        - ui_updater.clear_song_info should be called once
    """
    music_controller = MagicMock()
    ui_updater = MagicMock()
    handler = PlaybackHandler(music_controller, ui_updater)
    handler.stop()
    music_controller.stop_song.assert_called_once()
    ui_updater.clear_song_info.assert_called_once()


# --- NavigationHandler Tests ---


def test_navigation_handler_default_strategy():
    """
    Test that NavigationHandler initializes with NormalNavigationStrategy by default.

    This test verifies that when a NavigationHandler is instantiated without
    explicitly providing a strategy, it defaults to using NormalNavigationStrategy.

    Expected behavior:
        - The handler's navigation_strategy attribute should be an instance of
          NormalNavigationStrategy
    """
    handler = NavigationHandler()
    assert isinstance(handler.navigation_strategy, NormalNavigationStrategy)


def test_navigation_handler_set_strategy():
    """
    Test that NavigationHandler.set_strategy correctly updates the navigation strategy.

    This test verifies that when set_strategy is called with a new strategy,
    the handler's navigation_strategy attribute is updated accordingly.

    Expected behavior:
        - After calling set_strategy with a RandomNavigationStrategy instance,
          the handler's navigation_strategy attribute should be that instance
    """
    handler = NavigationHandler()
    handler.set_strategy(RandomNavigationStrategy())
    assert isinstance(handler.navigation_strategy, RandomNavigationStrategy)


def test_navigation_handler_next_index_normal():
    """
    Test get_next_index behavior with NormalNavigationStrategy.

    This test verifies that when using NormalNavigationStrategy, get_next_index
    correctly advances to the next index and wraps around at the end of the list.

    Expected behavior:
        - For index 0 in a list of 3 items, the next index should be 1
        - For index 2 in a list of 3 items, the next index should wrap to 0
    """
    handler = NavigationHandler(NormalNavigationStrategy())
    assert handler.get_next_index(0, 3) == 1
    assert handler.get_next_index(2, 3) == 0


def test_navigation_handler_previous_index_normal():
    """
    Test get_previous_index behavior with NormalNavigationStrategy.

    This test verifies that when using NormalNavigationStrategy, get_previous_index
    correctly goes to the previous index and wraps around at the beginning of the list.

    Expected behavior:
        - For index 1 in a list of 3 items, the previous index should be 0
        - For index 0 in a list of 3 items, the previous index should wrap to 2
    """
    handler = NavigationHandler(NormalNavigationStrategy())
    assert handler.get_previous_index(1, 3) == 0
    assert handler.get_previous_index(0, 3) == 2


def test_navigation_handler_next_index_random(monkeypatch):
    """
    Test get_next_index behavior with RandomNavigationStrategy.

    This test verifies that when using RandomNavigationStrategy, get_next_index
    generates random indices using the random module.

    Args:
        monkeypatch (pytest.MonkeyPatch): Pytest fixture for patching functions
                                         during tests.

    Expected behavior:
        - The random.randint function should be called to generate indices
        - The returned value should match the side_effect sequence defined
    """
    handler = NavigationHandler(RandomNavigationStrategy())
    mock_randint = MagicMock(side_effect=[0, 1])
    monkeypatch.setattr(
        "interfaces.navigation.navigation.secrets.randbelow", mock_randint
    )

    assert handler.get_next_index(0, 3) == 1
    assert mock_randint.call_count == 2


def test_navigation_handler_next_index_looping():
    """
    Test get_next_index behavior with LoopingNavigationStrategy.

    This test verifies that when using LoopingNavigationStrategy, get_next_index
    returns the same index, effectively "looping" the current song.

    Expected behavior:
        - For any input index, the output should be the same index
    """
    handler = NavigationHandler(LoopingNavigationStrategy())
    assert handler.get_next_index(1, 3) == 1


# --- UIEventHandler Tests ---


def test_ui_event_handler_add_songs(mock_ui):
    """
    Test UIEventHandler.handle_add_songs successfully adds songs to the list.

    This test verifies that when handle_add_songs is called and files are selected
    via the file dialog, they are correctly added to the UI list with proper formatting.

    Args:
        mock_ui (MagicMock): The mock UI object created by the mock_ui fixture.

    Expected behavior:
        - QFileDialog.getOpenFileNames should be called to prompt for file selection
        - The selected file should be added to the loaded_songs_listWidget
        - The item added should have the correct file path as user data
        - The item text should be the file name extracted from the path
    """
    db_manager = MagicMock()
    handler = UIEventHandler(mock_ui, db_manager)
    with patch.object(
        QFileDialog, "getOpenFileNames", return_value=(["/path/to/song.mp3"], "")
    ):
        handler.handle_add_songs()
        mock_ui.loaded_songs_listWidget.addItem.assert_called_once()
        item = mock_ui.loaded_songs_listWidget.addItem.call_args[0][0]
        assert item.data(Qt.UserRole) == "/path/to/song.mp3"
        assert item.text() == "song.mp3"


def test_ui_event_handler_add_songs_no_selection(mock_ui):
    """
    Test UIEventHandler.handle_add_songs when no files are selected.

    This test verifies that when handle_add_songs is called but no files are
    selected via the file dialog, an appropriate message is shown and no items
    are added to the list.

    Args:
        mock_ui (MagicMock): The mock UI object created by the mock_ui fixture.

    Expected behavior:
        - QFileDialog.getOpenFileNames should be called to prompt for file selection
        - When no files are selected, a message should be shown via MessageManager
        - No items should be added to the loaded_songs_listWidget
    """
    db_manager = MagicMock()
    handler = UIEventHandler(mock_ui, db_manager)
    with patch.object(QFileDialog, "getOpenFileNames", return_value=([], "")):
        with patch("utils.message_manager.MessageManager.show_info") as mock_show_info:
            handler.handle_add_songs()
            mock_show_info.assert_called_once_with(
                mock_ui, msg.TTL_INF, msg.MSG_NO_FILES_SEL
            )
            mock_ui.loaded_songs_listWidget.addItem.assert_not_called()


# --- EventHandler Tests ---


def test_event_handler_init(event_handler, mock_config):
    """
    Test that the EventHandler initializes properly with the correct handlers and connections.

    Args:
        event_handler: The EventHandler instance being tested
        mock_config: A mock configuration object containing UI and music_controller

    Verifies:
        - UI handler is properly instantiated
        - Playback handler is properly instantiated
        - Navigation handler is properly instantiated
        - UI reference is correctly set
        - Music controller reference is correctly set
        - Signal connections are properly established
    """
    assert isinstance(event_handler.ui_handler, UIEventHandler)
    assert isinstance(event_handler.playback_handler, PlaybackHandler)
    assert isinstance(event_handler.navigation_handler, NavigationHandler)
    assert event_handler.ui == mock_config.ui
    assert event_handler.music_controller == mock_config.music_controller
    mock_config.ui.add_songs_btn.clicked.connect.assert_called()


# --- on_delete_selected_song_clicked Tests ---


def test_on_delete_selected_song_empty_list(event_handler):
    """
    Test the on_delete_selected_song_clicked method's behavior with an empty song list.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - When list is empty, no actions are performed
        - Media player's stop method is not called
    """
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=False,
    ):
        event_handler.on_delete_selected_song_clicked()
        event_handler.music_controller.media_player().stop.assert_not_called()


def test_on_delete_selected_song_playing(event_handler):
    """
    Test the on_delete_selected_song_clicked method when the song to be deleted is currently playing.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Playback is stopped before deletion
        - The item is properly removed from the list widget
        - Current row is properly reset
        - Playback is restarted after deletion
    """
    list_widget = MagicMock(spec=QListWidget)
    list_widget.count.return_value = 2
    item = MagicMock(spec=QListWidgetItem)
    item.data.return_value = "/path/to/song.mp3"
    list_widget.currentItem.return_value = item
    list_widget.row.return_value = 0
    event_handler.list_manager.get_current_widget.return_value = list_widget
    event_handler.list_manager.get_selected_song.return_value = "/path/to/song.mp3"
    media_player = event_handler.music_controller.media_player()
    media_player.state.return_value = QMediaPlayer.PlayingState
    media_player.media.return_value.canonicalUrl.return_value.toLocalFile.return_value = (
        "/path/to/song.mp3"
    )
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.event_handler.list_validator.check_item_selected",
            return_value=True,
        ):
            with patch.object(event_handler.playback_handler, "stop") as mock_stop:
                with patch.object(event_handler.playback_handler, "play") as mock_play:
                    event_handler.on_delete_selected_song_clicked()
                    mock_stop.assert_called_once()
                    list_widget.takeItem.assert_called_once_with(0)
                    list_widget.setCurrentRow.assert_called_once_with(0)
                    mock_play.assert_called_once()


def test_on_delete_selected_song_no_selection(event_handler):
    """
    Test the on_delete_selected_song_clicked method's behavior when no song is selected.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Warning message is displayed to the user
        - No stop action is performed
        - No deletion is performed
    """
    list_widget = MagicMock(spec=QListWidget)
    list_widget.count.return_value = 1
    event_handler.list_manager.get_current_widget.return_value = list_widget
    event_handler.list_manager.get_selected_song.return_value = None
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.event_handler.list_validator.check_item_selected",
            return_value=True,
        ):
            with patch(
                "utils.message_manager.MessageManager.show_warning"
            ) as mock_warning:
                with patch.object(
                    event_handler.playback_handler, "stop", autospec=True
                ) as mock_stop:
                    event_handler.on_delete_selected_song_clicked()
                    mock_warning.assert_called_once_with(
                        event_handler.ui, msg.TTL_WRN, msg.MSG_NO_SONG_SEL
                    )
                    mock_stop.assert_not_called()


def test_on_delete_selected_song_not_playing(event_handler):
    """
    Test the on_delete_selected_song_clicked method when the song to be deleted is not currently playing.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Playback is stopped as a precaution
        - The item is properly removed from the list widget
        - Current row is properly reset
        - Playback is not restarted after deletion
    """
    list_widget = MagicMock(spec=QListWidget)
    list_widget.count.return_value = 2
    item = MagicMock(spec=QListWidgetItem)
    item.data.return_value = "/path/to/song.mp3"
    list_widget.currentItem.return_value = item
    list_widget.row.return_value = 0
    event_handler.list_manager.get_current_widget.return_value = list_widget
    event_handler.list_manager.get_selected_song.return_value = "/path/to/song.mp3"
    media_player = event_handler.music_controller.media_player()
    media_player.state.return_value = QMediaPlayer.StoppedState
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.event_handler.list_validator.check_item_selected",
            return_value=True,
        ):
            with patch.object(event_handler.playback_handler, "stop") as mock_stop:
                event_handler.on_delete_selected_song_clicked()
                mock_stop.assert_called_once()
                list_widget.takeItem.assert_called_once_with(0)
                list_widget.setCurrentRow.assert_called_once_with(0)


def test_on_delete_selected_song_operational_error(event_handler):
    """
    Test the on_delete_selected_song_clicked method's behavior when an operational database error occurs.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Critical error message is shown to the user
        - Error message contains the appropriate database error details
    """
    list_widget = MagicMock(spec=QListWidget)
    list_widget.count.return_value = 1
    item = MagicMock(spec=QListWidgetItem)
    item.data.return_value = "/path/to/song.mp3"
    list_widget.currentItem.return_value = item
    list_widget.row.return_value = 0
    event_handler.list_manager.get_current_widget.return_value = list_widget
    event_handler.list_manager.get_selected_song.return_value = "/path/to/song.mp3"
    event_handler.ui.current_playlist = "test_playlist"
    event_handler.ui.db_manager.delete_song.side_effect = OperationalError("DB error")
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.event_handler.list_validator.check_item_selected",
            return_value=True,
        ):
            with patch(
                "utils.message_manager.MessageManager.show_critical"
            ) as mock_critical:
                event_handler.on_delete_selected_song_clicked()
                mock_critical.assert_called_once_with(
                    event_handler.ui,
                    msg.TTL_ERR,
                    f"{msg.MSG_SONG_DEL_ERR} Database error: DB error",
                )


def test_on_delete_selected_song_runtime_error(event_handler):
    """
    Test the on_delete_selected_song_clicked method's behavior when a runtime error occurs.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Critical error message is shown to the user
        - Error message contains the appropriate runtime error details
    """
    list_widget = MagicMock(spec=QListWidget)
    list_widget.count.return_value = 1
    item = MagicMock(spec=QListWidgetItem)
    item.data.return_value = "/path/to/song.mp3"
    list_widget.currentItem.return_value = item
    list_widget.row.side_effect = RuntimeError("Widget error")
    event_handler.list_manager.get_current_widget.return_value = list_widget
    event_handler.list_manager.get_selected_song.return_value = "/path/to/song.mp3"
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.event_handler.list_validator.check_item_selected",
            return_value=True,
        ):
            with patch(
                "utils.message_manager.MessageManager.show_critical"
            ) as mock_critical:
                event_handler.on_delete_selected_song_clicked()
                mock_critical.assert_called_once_with(
                    event_handler.ui,
                    msg.TTL_ERR,
                    f"{msg.MSG_SONG_DEL_ERR} Widget error",
                )


def test_on_delete_selected_song_with_db_table(event_handler):
    """
    Test the on_delete_selected_song_clicked method when a specific database table is provided.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Database manager's delete_song method is called with the correct table name
        - The item is properly removed from the list widget
    """
    list_widget = MagicMock(spec=QListWidget)
    list_widget.count.return_value = 1
    item = MagicMock(spec=QListWidgetItem)
    item.data.return_value = "/path/to/song.mp3"
    list_widget.currentItem.return_value = item
    list_widget.row.return_value = 0
    event_handler.list_manager.get_current_widget.return_value = list_widget
    event_handler.list_manager.get_selected_song.return_value = "/path/to/song.mp3"
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.event_handler.list_validator.check_item_selected",
            return_value=True,
        ):
            event_handler.on_delete_selected_song_clicked(db_table="custom_table")
            event_handler.ui.db_manager.delete_song.assert_called_once_with(
                "custom_table", "/path/to/song.mp3"
            )
            list_widget.takeItem.assert_called_once_with(0)


# --- on_clear_list_clicked Tests ---


def test_on_clear_list_success(event_handler):
    """
    Test the on_clear_list_clicked method when user confirms clearing the list.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Confirmation dialog is shown to the user
        - On confirmation, playback is stopped
        - Current widget is cleared
    """
    list_widget = MagicMock(spec=QListWidget)
    list_widget.count.return_value = 1
    event_handler.list_manager.get_current_widget.return_value = list_widget
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch.object(
            event_handler.messanger, "show_question", return_value=QMessageBox.Yes
        ):
            with patch.object(event_handler.playback_handler, "stop") as mock_stop:
                event_handler.on_clear_list_clicked()
                mock_stop.assert_called_once()
                event_handler.list_manager.clear_current_widget.assert_called_once()


def test_on_clear_list_no_confirmation(event_handler):
    """
    Test the on_clear_list_clicked method when user declines clearing the list.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Confirmation dialog is shown to the user
        - On declination, no actions are performed
        - Playback is not stopped
        - Current widget is not cleared
    """
    list_widget = MagicMock(spec=QListWidget)
    list_widget.count.return_value = 1
    event_handler.list_manager.get_current_widget.return_value = list_widget
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch.object(
            event_handler.messanger, "show_question", return_value=QMessageBox.No
        ):
            with patch.object(event_handler.playback_handler, "stop") as mock_stop:
                event_handler.on_clear_list_clicked()
                mock_stop.assert_not_called()
                event_handler.list_manager.clear_current_widget.assert_not_called()


def test_on_clear_list_operational_error(event_handler):
    """
    Test the on_clear_list_clicked method's behavior when an operational database error occurs.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Critical error message is shown to the user
        - Error message contains the appropriate database error details
    """
    list_widget = MagicMock(spec=QListWidget)
    list_widget.count.return_value = 1
    event_handler.list_manager.get_current_widget.return_value = list_widget
    event_handler.ui.current_playlist = "test_playlist"
    event_handler.db_manager.delete_all_songs.side_effect = OperationalError("DB error")
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch.object(
            event_handler.messanger, "show_question", return_value=QMessageBox.Yes
        ):
            with patch(
                "utils.message_manager.MessageManager.show_critical"
            ) as mock_critical:
                event_handler.on_clear_list_clicked()
                mock_critical.assert_called_once_with(
                    event_handler.ui,
                    msg.TTL_ERR,
                    f"{msg.MSG_ALL_SONG_DEL_ERR} Database error: DB error",
                )


def test_on_clear_list_with_db_table(event_handler):
    """
    Test the on_clear_list_clicked method when a specific database table is provided.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Confirmation dialog is shown to the user
        - On confirmation, playback is stopped
        - Database manager's delete_all_songs method is called with the correct table name
    """
    list_widget = MagicMock(spec=QListWidget)
    list_widget.count.return_value = 1
    event_handler.list_manager.get_current_widget.return_value = list_widget
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch.object(
            event_handler.messanger, "show_question", return_value=QMessageBox.Yes
        ):
            with patch.object(event_handler.playback_handler, "stop") as mock_stop:
                event_handler.on_clear_list_clicked(db_table="custom_table")
                mock_stop.assert_called_once()
                event_handler.db_manager.delete_all_songs.assert_called_once_with(
                    "custom_table"
                )


# --- on_play_clicked Tests ---


def test_on_play_clicked_success(event_handler):
    """
    Test the on_play_clicked method when a valid song is selected.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Check for non-empty list and selected item passes
        - Playback handler's play method is called with the correct song path
    """
    list_widget = MagicMock(spec=QListWidget)
    list_widget.count.return_value = 1
    event_handler.list_manager.get_current_widget.return_value = list_widget
    event_handler.list_manager.get_selected_song.return_value = "/path/to/song.mp3"
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.event_handler.list_validator.check_item_selected",
            return_value=True,
        ):
            with patch.object(event_handler.playback_handler, "play") as mock_play:
                event_handler.on_play_clicked()
                mock_play.assert_called_once_with("/path/to/song.mp3")


def test_on_play_clicked_empty_list(event_handler):
    """
    Test the on_play_clicked method's behavior with an empty song list.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Check for non-empty list fails
        - Playback handler's play method is not called
    """
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=False,
    ):
        with patch.object(event_handler.playback_handler, "play") as mock_play:
            event_handler.on_play_clicked()
            mock_play.assert_not_called()


def test_on_play_clicked_no_selection(event_handler):
    """
    Test the on_play_clicked method when no song is selected in a non-empty list.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Check for non-empty list passes
        - Check for selected item fails
        - Playback handler's play method is not called
    """
    list_widget = MagicMock(spec=QListWidget)
    list_widget.count.return_value = 1
    event_handler.list_manager.get_current_widget.return_value = list_widget
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.event_handler.list_validator.check_item_selected",
            return_value=False,
        ):
            with patch.object(event_handler.playback_handler, "play") as mock_play:
                event_handler.on_play_clicked()
                mock_play.assert_not_called()


def test_on_play_clicked_no_song_path(event_handler):
    """
    Test the on_play_clicked method when get_selected_song returns None.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Check for non-empty list and selected item passes
        - Warning message is displayed due to missing song path
        - No attempt to play the song is made
    """
    list_widget = MagicMock(spec=QListWidget)
    list_widget.count.return_value = 1
    event_handler.list_manager.get_current_widget.return_value = list_widget
    event_handler.list_manager.get_selected_song.return_value = None
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.event_handler.list_validator.check_item_selected",
            return_value=True,
        ):
            with patch(
                "utils.message_manager.MessageManager.show_warning"
            ) as mock_warning:
                event_handler.on_play_clicked()
                mock_warning.assert_called_once_with(
                    event_handler.ui, msg.TTL_WRN, msg.MSG_NO_SONG_SEL
                )


def test_on_play_clicked_runtime_error(event_handler):
    """
    Test the on_play_clicked method's behavior when a runtime error occurs during playback.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Critical error message is shown to the user
        - Error message contains the appropriate runtime error details
    """
    list_widget = MagicMock(spec=QListWidget)
    list_widget.count.return_value = 1
    event_handler.list_manager.get_current_widget.return_value = list_widget
    event_handler.list_manager.get_selected_song.return_value = "/path/to/song.mp3"
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.event_handler.list_validator.check_item_selected",
            return_value=True,
        ):
            with patch.object(
                event_handler.playback_handler,
                "play",
                side_effect=RuntimeError("Play error"),
            ):
                with patch(
                    "utils.message_manager.MessageManager.show_critical"
                ) as mock_critical:
                    event_handler.on_play_clicked()
                    mock_critical.assert_called_once_with(
                        event_handler.ui, msg.TTL_ERR, f"{msg.MSG_PLAY_ERR} Play error"
                    )


# --- on_pause_clicked Tests ---


def test_on_pause_clicked(event_handler):
    """
    Test the on_pause_clicked method correctly calls the pause function.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Playback handler's pause method is called exactly once
    """
    with patch.object(event_handler.playback_handler, "pause") as mock_pause:
        event_handler.on_pause_clicked()
        mock_pause.assert_called_once()


# --- on_next_previous_clicked Tests ---


def test_on_next_previous_clicked_forward(event_handler):
    """
    Test the on_next_previous_clicked method for forward navigation.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - List's current row is set to the next item (row index + 1)
        - Playback handler's play method is called to play the next song
    """
    list_widget = MagicMock(spec=QListWidget)
    list_widget.count.return_value = 3
    list_widget.currentRow.return_value = 1
    event_handler.list_manager.get_current_widget.return_value = list_widget
    event_handler.list_manager.get_selected_song.return_value = "/path/to/song.mp3"
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.event_handler.list_validator.check_item_selected",
            return_value=True,
        ):
            with patch.object(event_handler.playback_handler, "play") as mock_play:
                event_handler.on_next_previous_clicked(direction="forward")
                list_widget.setCurrentRow.assert_called_once_with(2)
                mock_play.assert_called_once()


def test_on_next_previous_clicked_backward(event_handler):
    """
    Test the on_next_previous_clicked method for backward navigation.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - List's current row is set to the previous item (row index - 1)
        - Playback handler's play method is called to play the previous song
    """
    list_widget = MagicMock(spec=QListWidget)
    list_widget.count.return_value = 3
    list_widget.currentRow.return_value = 1
    event_handler.list_manager.get_current_widget.return_value = list_widget
    event_handler.list_manager.get_selected_song.return_value = "/path/to/song.mp3"
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.event_handler.list_validator.check_item_selected",
            return_value=True,
        ):
            with patch.object(event_handler.playback_handler, "play") as mock_play:
                event_handler.on_next_previous_clicked(direction="backward")
                list_widget.setCurrentRow.assert_called_once_with(0)
                mock_play.assert_called_once()


def test_on_next_previous_clicked_invalid_direction(event_handler):
    """
    Test the on_next_previous_clicked method's behavior with an invalid direction parameter.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - List's current row remains unchanged
        - Playback handler's play method is still called with the current song
    """
    list_widget = MagicMock(spec=QListWidget)
    list_widget.count.return_value = 3
    list_widget.currentRow.return_value = 1
    event_handler.list_manager.get_current_widget.return_value = list_widget
    event_handler.list_manager.get_selected_song.return_value = "/path/to/song.mp3"
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.event_handler.list_validator.check_item_selected",
            return_value=True,
        ):
            with patch.object(event_handler.playback_handler, "play") as mock_play:
                event_handler.on_next_previous_clicked(direction="invalid")
                list_widget.setCurrentRow.assert_called_once_with(1)  # Stays the same
                mock_play.assert_called_once()


def test_on_next_previous_clicked_empty_list(event_handler):
    """
    Test the on_next_previous_clicked method's behavior with an empty song list.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Check for non-empty list fails
        - Playback handler's play method is not called
    """
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=False,
    ):
        with patch.object(event_handler.playback_handler, "play") as mock_play:
            event_handler.on_next_previous_clicked()
            mock_play.assert_not_called()


def test_on_next_previous_clicked_runtime_error(event_handler):
    """
    Test the on_next_previous_clicked method's behavior when a runtime error occurs.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Critical error message is shown to the user
        - Error message contains the appropriate runtime error details
    """
    list_widget = MagicMock(spec=QListWidget)
    list_widget.count.return_value = 3
    list_widget.currentRow.side_effect = RuntimeError("Row error")
    event_handler.list_manager.get_current_widget.return_value = list_widget
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.event_handler.list_validator.check_item_selected",
            return_value=True,
        ):
            with patch(
                "utils.message_manager.MessageManager.show_critical"
            ) as mock_critical:
                event_handler.on_next_previous_clicked()
                mock_critical.assert_called_once_with(
                    event_handler.ui, msg.TTL_ERR, f"{msg.MSG_NAV_ERR} Row error"
                )


# --- on_loop_clicked Tests ---


def test_on_loop_clicked_enable(event_handler):
    """
    Test the on_loop_clicked method when enabling loop mode.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Loop flag is set to True
        - Shuffle button is disabled to prevent concurrent modes
        - Navigation strategy is changed to LoopingNavigationStrategy
    """
    event_handler.music_controller.is_looped = False
    event_handler.on_loop_clicked()
    assert event_handler.music_controller.is_looped is True
    event_handler.ui.shuffle_songs_btn.setEnabled.assert_called_once_with(False)
    assert isinstance(
        event_handler.navigation_handler.navigation_strategy, LoopingNavigationStrategy
    )


def test_on_loop_clicked_disable(event_handler):
    """
    Test the on_loop_clicked method when disabling loop mode.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Loop flag is set to False
        - Shuffle button is re-enabled
        - Navigation strategy is changed back to NormalNavigationStrategy
    """
    event_handler.music_controller.is_looped = True
    event_handler.on_loop_clicked()
    assert event_handler.music_controller.is_looped is False
    event_handler.ui.shuffle_songs_btn.setEnabled.assert_called_once_with(True)
    assert isinstance(
        event_handler.navigation_handler.navigation_strategy, NormalNavigationStrategy
    )


def test_on_loop_clicked_runtime_error(event_handler):
    """
    Test the on_loop_clicked method's behavior when a runtime error occurs.

    Args:
        event_handler: The EventHandler instance being tested

    Verifies:
        - Critical error message is shown to the user
        - Error message contains the appropriate runtime error details
    """
    event_handler.music_controller.is_looped = False
    with patch.object(
        event_handler.navigation_handler,
        "set_strategy",
        side_effect=RuntimeError("Strategy error"),
    ):
        with patch(
            "utils.message_manager.MessageManager.show_critical"
        ) as mock_critical:
            event_handler.on_loop_clicked()
            mock_critical.assert_called_once_with(
                event_handler.ui, msg.TTL_ERR, f"{msg.MSG_LOOP_ERR} Strategy error"
            )


# --- on_shuffle_clicked Tests ---


def test_on_shuffle_clicked_enable(event_handler):
    """
    Test that on_shuffle_clicked method enables shuffling functionality.

    This test verifies that when shuffle is currently disabled and the shuffle button is clicked,
    the following actions occur:
    1. The is_shuffled flag gets set to True
    2. The loop_one button is disabled
    3. The navigation strategy is changed to RandomNavigationStrategy

    Args:
        event_handler: A fixture providing the event handler instance with mocked dependencies

    Returns:
        None
    """
    event_handler.music_controller.is_shuffled = False
    event_handler.on_shuffle_clicked()
    assert event_handler.music_controller.is_shuffled is True
    event_handler.ui.loop_one_btn.setEnabled.assert_called_once_with(False)
    assert isinstance(
        event_handler.navigation_handler.navigation_strategy, RandomNavigationStrategy
    )


def test_on_shuffle_clicked_disable(event_handler):
    """
    Test that on_shuffle_clicked method disables shuffling functionality.

    This test verifies that when shuffle is currently enabled and the shuffle button is clicked,
    the following actions occur:
    1. The is_shuffled flag gets set to False
    2. The loop_one button is enabled
    3. The navigation strategy is changed to NormalNavigationStrategy

    Args:
        event_handler: A fixture providing the event handler instance with mocked dependencies

    Returns:
        None
    """
    event_handler.music_controller.is_shuffled = True
    event_handler.on_shuffle_clicked()
    assert event_handler.music_controller.is_shuffled is False
    event_handler.ui.loop_one_btn.setEnabled.assert_called_once_with(True)
    assert isinstance(
        event_handler.navigation_handler.navigation_strategy, NormalNavigationStrategy
    )


def test_on_shuffle_clicked_runtime_error(event_handler):
    """
    Test that on_shuffle_clicked method handles RuntimeError properly.

    This test verifies that when a RuntimeError occurs during the strategy change,
    the application shows a critical error message to the user containing the error details.

    Args:
        event_handler: A fixture providing the event handler instance with mocked dependencies

    Returns:
        None
    """
    event_handler.music_controller.is_shuffled = False
    with patch.object(
        event_handler.navigation_handler,
        "set_strategy",
        side_effect=RuntimeError("Strategy error"),
    ):
        with patch(
            "utils.message_manager.MessageManager.show_critical"
        ) as mock_critical:
            event_handler.on_shuffle_clicked()
            mock_critical.assert_called_once_with(
                event_handler.ui, msg.TTL_ERR, f"{msg.MSG_SHFL_ERR} Strategy error"
            )


# --- on_volume_clicked Tests ---


def test_on_volume_clicked_valid(event_handler):
    """
    Test that on_volume_clicked method processes valid volume values correctly.

    This test verifies that when a valid volume value (integer between 0-100) is provided:
    1. The music controller's set_volume method is called with the correct value
    2. The UI volume label is updated to display the new volume value

    Args:
        event_handler: A fixture providing the event handler instance with mocked dependencies

    Returns:
        None
    """
    event_handler.on_volume_clicked(50)
    event_handler.music_controller.set_volume.assert_called_once_with(50)
    event_handler.ui.volume_label.setText.assert_called_once_with("50")


def test_on_volume_clicked_invalid_value(event_handler):
    """
    Test that on_volume_clicked method handles invalid volume values correctly.

    This test verifies that when an invalid volume value (out of 0-100 range) is provided:
    1. A critical error message is shown to the user
    2. The music controller's set_volume method is not called

    Args:
        event_handler: A fixture providing the event handler instance with mocked dependencies

    Returns:
        None
    """
    with patch("utils.message_manager.MessageManager.show_critical") as mock_critical:
        event_handler.on_volume_clicked(-1)
        mock_critical.assert_called_once_with(
            event_handler.ui,
            msg.TTL_ERR,
            f"{msg.MSG_VOL_ERR} Volume value must be between 0 and 100",
        )
        event_handler.music_controller.set_volume.assert_not_called()


def test_on_volume_clicked_non_integer(event_handler):
    """
    Test that on_volume_clicked method handles non-integer volume values correctly.

    This test verifies that when a non-integer volume value is provided:
    1. A critical error message is shown to the user
    2. The music controller's set_volume method is not called

    Args:
        event_handler: A fixture providing the event handler instance with mocked dependencies

    Returns:
        None
    """
    with patch("utils.message_manager.MessageManager.show_critical") as mock_critical:
        event_handler.on_volume_clicked("50")
        mock_critical.assert_called_once_with(
            event_handler.ui,
            msg.TTL_ERR,
            f"{msg.MSG_VOL_ERR} Volume value must be between 0 and 100",
        )
        event_handler.music_controller.set_volume.assert_not_called()


def test_on_volume_clicked_runtime_error(event_handler):
    """
    Test that on_volume_clicked method handles RuntimeError correctly.

    This test verifies that when the music controller's set_volume method raises a RuntimeError:
    1. A critical error message is shown to the user containing the error details

    Args:
        event_handler: A fixture providing the event handler instance with mocked dependencies

    Returns:
        None
    """
    event_handler.music_controller.set_volume.side_effect = RuntimeError("Volume error")
    with patch("utils.message_manager.MessageManager.show_critical") as mock_critical:
        event_handler.on_volume_clicked(50)
        mock_critical.assert_called_once_with(
            event_handler.ui, msg.TTL_ERR, f"{msg.MSG_VOL_ERR} Volume error"
        )


# --- handle_media_status Tests ---


def test_handle_media_status_end(event_handler):
    """
    Test that handle_media_status method properly handles EndOfMedia status.

    This test verifies that when the media player signals EndOfMedia status:
    1. The event handler calls on_next_previous_clicked to play the next track

    Args:
        event_handler: A fixture providing the event handler instance with mocked dependencies

    Returns:
        None
    """
    with patch.object(event_handler, "on_next_previous_clicked") as mock_next:
        event_handler.handle_media_status(QMediaPlayer.EndOfMedia)
        mock_next.assert_called_once_with()

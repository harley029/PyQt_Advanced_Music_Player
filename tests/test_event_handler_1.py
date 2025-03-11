# pylint: disable=redefined-outer-name
from unittest.mock import MagicMock, patch
import pytest
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QFileDialog, QMessageBox
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtCore import Qt
from sqlite3 import OperationalError

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
    """Mock UI object with necessary widgets and attributes."""
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
    """Mock EventHandlerConfig with all dependencies и постоянным патчем для ListManager."""
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
    """Fixture for EventHandler instance."""
    return EventHandler(mock_config)


# --- PlaybackHandler Tests ---


def test_playback_handler_play():
    """Test PlaybackHandler.play calls music_controller and ui_updater."""
    music_controller = MagicMock()
    ui_updater = MagicMock()
    handler = PlaybackHandler(music_controller, ui_updater)
    handler.play("/path/to/song.mp3")
    music_controller.play_song.assert_called_once_with("/path/to/song.mp3")
    ui_updater.update_current_song_info.assert_called_once_with("/path/to/song.mp3")


def test_playback_handler_pause_playing():
    """Test PlaybackHandler.pause when song is playing."""
    music_controller = MagicMock()
    ui_updater = MagicMock()
    music_controller.is_playing.return_value = True
    handler = PlaybackHandler(music_controller, ui_updater)
    handler.pause()
    music_controller.pause_song.assert_called_once()
    music_controller.resume_song.assert_not_called()


def test_playback_handler_pause_paused():
    """Test PlaybackHandler.pause when song is paused."""
    music_controller = MagicMock()
    ui_updater = MagicMock()
    music_controller.is_playing.return_value = False
    music_controller.is_paused.return_value = True
    handler = PlaybackHandler(music_controller, ui_updater)
    handler.pause()
    music_controller.resume_song.assert_called_once()
    music_controller.pause_song.assert_not_called()


def test_playback_handler_stop():
    """Test PlaybackHandler.stop calls music_controller and ui_updater."""
    music_controller = MagicMock()
    ui_updater = MagicMock()
    handler = PlaybackHandler(music_controller, ui_updater)
    handler.stop()
    music_controller.stop_song.assert_called_once()
    ui_updater.clear_song_info.assert_called_once()


# --- NavigationHandler Tests ---


def test_navigation_handler_default_strategy():
    """Test NavigationHandler initializes with NormalNavigationStrategy."""
    handler = NavigationHandler()
    assert isinstance(handler.navigation_strategy, NormalNavigationStrategy)


def test_navigation_handler_set_strategy():
    """Test NavigationHandler.set_strategy updates the strategy."""
    handler = NavigationHandler()
    handler.set_strategy(RandomNavigationStrategy())
    assert isinstance(handler.navigation_strategy, RandomNavigationStrategy)


def test_navigation_handler_next_index_normal():
    """Test get_next_index with NormalNavigationStrategy."""
    handler = NavigationHandler(NormalNavigationStrategy())
    assert handler.get_next_index(0, 3) == 1
    assert handler.get_next_index(2, 3) == 0  # Wrap-around


def test_navigation_handler_previous_index_normal():
    """Test get_previous_index with NormalNavigationStrategy."""
    handler = NavigationHandler(NormalNavigationStrategy())
    assert handler.get_previous_index(1, 3) == 0
    assert handler.get_previous_index(0, 3) == 2  # Wrap-around


def test_navigation_handler_next_index_random(monkeypatch):
    """Test get_next_index with RandomNavigationStrategy."""
    handler = NavigationHandler(RandomNavigationStrategy())
    mock_randint = MagicMock(side_effect=[0, 1])
    monkeypatch.setattr("interfaces.navigation.navigation.randint", mock_randint)
    assert handler.get_next_index(0, 3) == 1
    assert mock_randint.call_count == 2


def test_navigation_handler_next_index_looping():
    """Test get_next_index with LoopingNavigationStrategy."""
    handler = NavigationHandler(LoopingNavigationStrategy())
    assert handler.get_next_index(1, 3) == 1


# --- UIEventHandler Tests ---


def test_ui_event_handler_add_songs(mock_ui):
    """Test UIEventHandler.handle_add_songs adds songs."""
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
    """Test UIEventHandler.handle_add_songs with no files selected."""
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
    """Test EventHandler initializes handlers and connects signals."""
    assert isinstance(event_handler.ui_handler, UIEventHandler)
    assert isinstance(event_handler.playback_handler, PlaybackHandler)
    assert isinstance(event_handler.navigation_handler, NavigationHandler)
    assert event_handler.ui == mock_config.ui
    assert event_handler.music_controller == mock_config.music_controller
    mock_config.ui.add_songs_btn.clicked.connect.assert_called()


# --- on_delete_selected_song_clicked Tests ---


def test_on_delete_selected_song_empty_list(event_handler):
    """Test on_delete_selected_song_clicked with empty list."""
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=False,
    ):
        event_handler.on_delete_selected_song_clicked()
        event_handler.music_controller.media_player().stop.assert_not_called()


def test_on_delete_selected_song_playing(event_handler):
    """Test on_delete_selected_song_clicked when song is playing."""
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
    """Test on_delete_selected_song_clicked with no song selected."""
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
                # Explicitly patch playback_handler.stop to ensure it’s a MagicMock
                with patch.object(
                    event_handler.playback_handler, "stop", autospec=True
                ) as mock_stop:
                    event_handler.on_delete_selected_song_clicked()
                    mock_warning.assert_called_once_with(
                        event_handler.ui, msg.TTL_WRN, msg.MSG_NO_SONG_SEL
                    )
                    mock_stop.assert_not_called()


def test_on_delete_selected_song_not_playing(event_handler):
    """Test on_delete_selected_song_clicked when song is not playing."""
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
    """Test on_delete_selected_song_clicked with OperationalError."""
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
    """Test on_delete_selected_song_clicked with RuntimeError."""
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
    """Test on_delete_selected_song_clicked with explicit db_table."""
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
    """Test on_clear_list_clicked with confirmation."""
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
    """Test on_clear_list_clicked with no confirmation."""
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
    """Test on_clear_list_clicked with OperationalError."""
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
    """Test on_clear_list_clicked with explicit db_table."""
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
    """Test on_play_clicked with valid selection."""
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
    """Test on_play_clicked with empty list."""
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=False,
    ):
        with patch.object(event_handler.playback_handler, "play") as mock_play:
            event_handler.on_play_clicked()
            mock_play.assert_not_called()


def test_on_play_clicked_no_selection(event_handler):
    """Test on_play_clicked with no item selected."""
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
    """Test on_play_clicked with no song path."""
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
    """Test on_play_clicked with RuntimeError."""
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
    """Test on_pause_clicked calls playback_handler.pause."""
    with patch.object(event_handler.playback_handler, "pause") as mock_pause:
        event_handler.on_pause_clicked()
        mock_pause.assert_called_once()


# --- on_next_previous_clicked Tests ---


def test_on_next_previous_clicked_forward(event_handler):
    """Test on_next_previous_clicked for forward navigation."""
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
    """Test on_next_previous_clicked for backward navigation."""
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
    """Test on_next_previous_clicked with invalid direction."""
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
    """Test on_next_previous_clicked with empty list."""
    with patch(
        "controllers.event_handler.list_validator.check_list_not_empty",
        return_value=False,
    ):
        with patch.object(event_handler.playback_handler, "play") as mock_play:
            event_handler.on_next_previous_clicked()
            mock_play.assert_not_called()


def test_on_next_previous_clicked_runtime_error(event_handler):
    """Test on_next_previous_clicked with RuntimeError."""
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
    """Test on_loop_clicked enables looping."""
    event_handler.music_controller.is_looped = False
    event_handler.on_loop_clicked()
    assert event_handler.music_controller.is_looped is True
    event_handler.ui.shuffle_songs_btn.setEnabled.assert_called_once_with(False)
    assert isinstance(
        event_handler.navigation_handler.navigation_strategy, LoopingNavigationStrategy
    )


def test_on_loop_clicked_disable(event_handler):
    """Test on_loop_clicked disables looping."""
    event_handler.music_controller.is_looped = True
    event_handler.on_loop_clicked()
    assert event_handler.music_controller.is_looped is False
    event_handler.ui.shuffle_songs_btn.setEnabled.assert_called_once_with(True)
    assert isinstance(
        event_handler.navigation_handler.navigation_strategy, NormalNavigationStrategy
    )


def test_on_loop_clicked_runtime_error(event_handler):
    """Test on_loop_clicked with RuntimeError."""
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
    """Test on_shuffle_clicked enables shuffling."""
    event_handler.music_controller.is_shuffled = False
    event_handler.on_shuffle_clicked()
    assert event_handler.music_controller.is_shuffled is True
    event_handler.ui.loop_one_btn.setEnabled.assert_called_once_with(False)
    assert isinstance(
        event_handler.navigation_handler.navigation_strategy, RandomNavigationStrategy
    )


def test_on_shuffle_clicked_disable(event_handler):
    """Test on_shuffle_clicked disables shuffling."""
    event_handler.music_controller.is_shuffled = True
    event_handler.on_shuffle_clicked()
    assert event_handler.music_controller.is_shuffled is False
    event_handler.ui.loop_one_btn.setEnabled.assert_called_once_with(True)
    assert isinstance(
        event_handler.navigation_handler.navigation_strategy, NormalNavigationStrategy
    )


def test_on_shuffle_clicked_runtime_error(event_handler):
    """Test on_shuffle_clicked with RuntimeError."""
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
    """Test on_volume_clicked with valid value."""
    event_handler.on_volume_clicked(50)
    event_handler.music_controller.set_volume.assert_called_once_with(50)
    event_handler.ui.volume_label.setText.assert_called_once_with("50")


def test_on_volume_clicked_invalid_value(event_handler):
    """Test on_volume_clicked with invalid value."""
    with patch("utils.message_manager.MessageManager.show_critical") as mock_critical:
        event_handler.on_volume_clicked(-1)
        mock_critical.assert_called_once_with(
            event_handler.ui,
            msg.TTL_ERR,
            f"{msg.MSG_VOL_ERR} Volume value must be between 0 and 100",
        )
        event_handler.music_controller.set_volume.assert_not_called()


def test_on_volume_clicked_non_integer(event_handler):
    """Test on_volume_clicked with non-integer value."""
    with patch("utils.message_manager.MessageManager.show_critical") as mock_critical:
        event_handler.on_volume_clicked("50")
        mock_critical.assert_called_once_with(
            event_handler.ui,
            msg.TTL_ERR,
            f"{msg.MSG_VOL_ERR} Volume value must be between 0 and 100",
        )
        event_handler.music_controller.set_volume.assert_not_called()


def test_on_volume_clicked_runtime_error(event_handler):
    """Test on_volume_clicked with RuntimeError."""
    event_handler.music_controller.set_volume.side_effect = RuntimeError("Volume error")
    with patch("utils.message_manager.MessageManager.show_critical") as mock_critical:
        event_handler.on_volume_clicked(50)
        mock_critical.assert_called_once_with(
            event_handler.ui, msg.TTL_ERR, f"{msg.MSG_VOL_ERR} Volume error"
        )


# --- handle_media_status Tests ---


def test_handle_media_status_end(event_handler):
    """Test handle_media_status triggers next song on EndOfMedia."""
    with patch.object(event_handler, "on_next_previous_clicked") as mock_next:
        event_handler.handle_media_status(QMediaPlayer.EndOfMedia)
        mock_next.assert_called_once_with()

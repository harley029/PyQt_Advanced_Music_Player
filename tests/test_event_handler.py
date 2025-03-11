# test_event_handler.py
# pylint: disable=redefined-outer-name, duplicate-code

from sqlite3 import IntegrityError, OperationalError
from unittest.mock import MagicMock, patch

import pytest
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QMessageBox

from controllers.favourites_manager import FavouritesManager
from utils import messages as msg

from tests.test_utils import create_mock_music_controller, create_mock_ui_provider


@pytest.fixture
def mock_ui_provider():
    return create_mock_ui_provider()


@pytest.fixture
def mock_parent(mock_ui_provider):
    """
    Мок родительского объекта с необходимыми атрибутами:
      - db_manager с методами fetch_all_songs, add_song, delete_song, delete_all_songs
      - ui_provider
      - list_widget_provider с методом get_currently_selected_song
      - music_controller с media_player, stop_song и play_song
      - loaded_songs_listWidget и favourites_listWidget
      - current_playlist
    """
    ui_provider, favourites_widget, loaded_songs_widget = mock_ui_provider
    parent = MagicMock()
    parent.db_manager = MagicMock()
    parent.db_manager.fetch_all_songs.return_value = []
    parent.db_manager.add_song = MagicMock()
    parent.db_manager.delete_song = MagicMock()
    parent.db_manager.delete_all_songs = MagicMock()
    parent.ui_provider = ui_provider
    list_widget_provider = MagicMock()
    list_widget_provider.get_currently_selected_song.return_value = "song.mp3"
    parent.list_widget_provider = list_widget_provider
    parent.music_controller = create_mock_music_controller()
    parent.loaded_songs_listWidget = loaded_songs_widget
    parent.favourites_listWidget = favourites_widget
    parent.current_playlist = None
    return parent


@pytest.fixture
def fav_manager(mock_parent):
    return FavouritesManager(mock_parent)


# --- Тесты для load_favourites ---


def test_load_favourites_success(fav_manager):
    """Проверяет, что load_favourites очищает виджет и добавляет песни из БД."""
    songs = ["/music/song1.mp3", "/music/song2.mp3"]
    fav_manager.db_manager.fetch_all_songs.return_value = songs
    fav_manager.favourites_widget = MagicMock(spec=QListWidget)
    fav_manager.favourites_widget.clear = MagicMock()
    fav_manager.favourites_widget.addItem = MagicMock()

    fav_manager.load_favourites()

    fav_manager.favourites_widget.clear.assert_called_once()
    fav_manager.db_manager.fetch_all_songs.assert_called_once_with("favourites")
    assert fav_manager.favourites_widget.addItem.call_count == len(songs)


def test_load_favourites_db_error(fav_manager):
    """Если fetch_all_songs вызывает OperationalError, вызывается show_critical."""
    error = OperationalError("DB error")
    fav_manager.db_manager.fetch_all_songs.side_effect = error
    fav_manager.favourites_widget = MagicMock(spec=QListWidget)
    with patch.object(fav_manager.messanger, "show_critical") as mock_show_critical:
        fav_manager.load_favourites()
        mock_show_critical.assert_called_once()
        assert "DB error" in mock_show_critical.call_args[0][2]


# --- Тесты для add_to_favourites ---


def test_add_to_favourites_loaded_empty(fav_manager):
    """Если loaded_songs_widget пуст, add_to_favourites не вызывает добавление."""
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=False,
    ):
        fav_manager.add_to_favourites()
        fav_manager.db_manager.add_song.assert_not_called()


def test_add_to_favourites_no_item_selected(fav_manager):
    """Если check_item_selected возвращает False, add_to_favourites не добавляет песню."""
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.favourites_manager.list_validator.check_item_selected",
            return_value=False,
        ):
            fav_manager.add_to_favourites()
            fav_manager.db_manager.add_song.assert_not_called()


def test_add_to_favourites_no_current_song(fav_manager, mock_parent):
    """
    Если list_widget_provider.get_currently_selected_song возвращает None,
    вызывается show_warning и добавление не происходит.
    """
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.favourites_manager.list_validator.check_item_selected",
            return_value=True,
        ):
            mock_parent.list_widget_provider.get_currently_selected_song.return_value = (
                None
            )
            with patch.object(
                fav_manager.messanger, "show_warning"
            ) as mock_show_warning:
                fav_manager.add_to_favourites()
                fav_manager.db_manager.add_song.assert_not_called()
                mock_show_warning.assert_called_once()
                assert msg.MSG_NO_SONG_SEL in mock_show_warning.call_args[0][2]


def test_add_to_favourites_success(fav_manager):
    """При корректном выборе песни, add_to_favourites вызывает db_manager.add_song."""
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.favourites_manager.list_validator.check_item_selected",
            return_value=True,
        ):
            fav_manager.db_manager.add_song.side_effect = None
            fav_manager.add_to_favourites()
            fav_manager.db_manager.add_song.assert_called_once_with(
                "favourites", "song.mp3"
            )


def test_add_to_favourites_integrity_error(fav_manager):
    """Если db_manager.add_song выбрасывает IntegrityError, вызывается show_warning."""
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.favourites_manager.list_validator.check_item_selected",
            return_value=True,
        ):
            fav_manager.db_manager.add_song.side_effect = IntegrityError("duplicate")
            with patch.object(
                fav_manager.messanger, "show_warning"
            ) as mock_show_warning:
                fav_manager.add_to_favourites()
                mock_show_warning.assert_called_once()
                assert msg.MSG_FAV_EXIST in mock_show_warning.call_args[0][2]


def test_add_to_favourites_operational_error(fav_manager):
    """Если db_manager.add_song выбрасывает OperationalError, вызывается show_critical."""
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.favourites_manager.list_validator.check_item_selected",
            return_value=True,
        ):
            error = OperationalError("op error")
            fav_manager.db_manager.add_song.side_effect = error
            with patch.object(
                fav_manager.messanger, "show_critical"
            ) as mock_show_critical:
                fav_manager.add_to_favourites()
                mock_show_critical.assert_called_once()
                assert "op error" in mock_show_critical.call_args[0][2]


# --- Тесты для remove_selected_favourite ---


def test_remove_selected_favourite_empty_list(fav_manager, mock_parent):
    """Если favourites_widget пуст, remove_selected_favourite ничего не делает."""
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=False,
    ):
        fav_widget = MagicMock(spec=QListWidget)
        fav_widget.count.return_value = 0
        fav_manager.favourites_widget = fav_widget
        fav_manager.remove_selected_favourite()
        mock_parent.music_controller.stop_song.assert_not_called()
        fav_manager.db_manager.delete_song.assert_not_called()


def test_remove_selected_favourite_no_selection(fav_manager, mock_parent):
    """Если check_item_selected возвращает False, remove_selected_favourite не удаляет песню."""
    with patch(
        "controllers.favourites_manager.list_validator.check_item_selected",
        return_value=False,
    ):
        fav_widget = MagicMock(spec=QListWidget)
        fav_widget.count.return_value = 1
        fav_manager.favourites_widget = fav_widget
        fav_manager.remove_selected_favourite()
        mock_parent.music_controller.stop_song.assert_not_called()
        fav_manager.db_manager.delete_song.assert_not_called()


def test_remove_selected_favourite_not_playing(fav_manager, mock_parent):
    """
    Если удаляемая песня не является текущей, stop_song не вызывается.
    """
    fav_widget = MagicMock(spec=QListWidget)
    fav_widget.count.return_value = 1
    item = MagicMock(spec=QListWidgetItem)
    item.data.return_value = "song.mp3"
    fav_widget.item.return_value = item
    fav_widget.currentRow.return_value = 0
    fav_manager.favourites_widget = fav_widget
    with patch.object(
        fav_manager, "_get_current_playing_song", return_value="other_song.mp3"
    ):
        with patch(
            "controllers.favourites_manager.list_validator.check_list_not_empty",
            return_value=True,
        ):
            with patch(
                "controllers.favourites_manager.list_validator.check_item_selected",
                return_value=True,
            ):
                fav_manager.remove_selected_favourite()
    mock_parent.music_controller.stop_song.assert_not_called()
    fav_manager.db_manager.delete_song.assert_called_once_with("favourites", "song.mp3")
    fav_widget.takeItem.assert_called_once()


def test_remove_selected_favourite_playing_and_next(fav_manager, mock_parent):
    """
    Если удаляемая песня является текущей, вызывается stop_song, затем play_song следующей песни.
    """
    fav_widget = MagicMock(spec=QListWidget)
    fav_widget.count.side_effect = lambda: 2 if fav_widget.count.call_count <= 1 else 1
    item = MagicMock(spec=QListWidgetItem)
    item.data.return_value = "song.mp3"
    fav_widget.item.side_effect = lambda i: item
    fav_widget.currentRow.return_value = 0
    fav_manager.favourites_widget = fav_widget
    with patch.object(
        fav_manager, "_get_current_playing_song", return_value="song.mp3"
    ):
        with patch(
            "controllers.favourites_manager.list_validator.check_list_not_empty",
            return_value=True,
        ):
            with patch(
                "controllers.favourites_manager.list_validator.check_item_selected",
                return_value=True,
            ):
                with patch.object(
                    mock_parent.music_controller, "stop_song"
                ) as mock_stop:
                    with patch.object(
                        mock_parent.music_controller, "play_song"
                    ) as mock_play:
                        fav_manager.remove_selected_favourite()
                        mock_stop.assert_called_once()
                        fav_manager.db_manager.delete_song.assert_called_once_with(
                            "favourites", "song.mp3"
                        )
                        fav_widget.takeItem.assert_called_once()
                        mock_play.assert_called_once()


def test_remove_selected_favourite_db_error(fav_manager):
    """
    Если db_manager.delete_song выбрасывает OperationalError, вызывается show_critical.
    """
    fav_widget = MagicMock(spec=QListWidget)
    fav_widget.count.return_value = 1
    item = MagicMock(spec=QListWidgetItem)
    item.data.return_value = "song.mp3"
    fav_widget.item.return_value = item
    fav_widget.currentRow.return_value = 0
    fav_manager.favourites_widget = fav_widget
    error = OperationalError("DB delete error")
    fav_manager.db_manager.delete_song.side_effect = error
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch(
            "controllers.favourites_manager.list_validator.check_item_selected",
            return_value=True,
        ):
            with patch.object(
                fav_manager.messanger, "show_critical"
            ) as mock_show_critical:
                fav_manager.remove_selected_favourite()
                mock_show_critical.assert_called_once()
                assert "DB delete error" in mock_show_critical.call_args[0][2]


# --- Тесты для clear_favourites ---


def test_clear_favourites_list_empty(fav_manager):
    """
    Если check_list_not_empty возвращает False, clear_favourites не очищает список.
    """
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=False,
    ):
        fav_manager.favourites_widget = MagicMock(spec=QListWidget)
        fav_manager.clear_favourites()
        fav_manager.favourites_widget.clear.assert_not_called()


def test_clear_favourites_no_confirmation(fav_manager, mock_parent):
    """
    Если show_question возвращает не QMessageBox.Yes, clear_favourites не очищает список.
    """
    fav_widget = MagicMock(spec=QListWidget)
    fav_widget.count.return_value = 2
    fav_manager.favourites_widget = fav_widget
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch.object(
            fav_manager.messanger, "show_question", return_value=QMessageBox.No
        ):
            fav_manager.clear_favourites()
            mock_parent.music_controller.stop_song.assert_not_called()
            fav_widget.clear.assert_not_called()
            fav_manager.db_manager.delete_all_songs.assert_not_called()


def test_clear_favourites_success(fav_manager, mock_parent):
    """
    Если пользователь подтверждает удаление, clear_favourites вызывает stop_song (при совпадении текущей песни),
    очищает favourites_widget и вызывает db_manager.delete_all_songs.
    """
    fav_widget = MagicMock(spec=QListWidget)
    fav_widget.count.return_value = 2
    item = MagicMock(spec=QListWidgetItem)
    item.data.return_value = "song.mp3"
    fav_widget.item.side_effect = lambda i: item
    fav_manager.favourites_widget = fav_widget
    with patch.object(
        fav_manager, "_get_current_playing_song", return_value="song.mp3"
    ):
        with patch.object(
            fav_manager.messanger, "show_question", return_value=QMessageBox.Yes
        ):
            fav_manager.clear_favourites()
    mock_parent.music_controller.stop_song.assert_called_once()
    fav_widget.clear.assert_called_once()
    fav_manager.db_manager.delete_all_songs.assert_called_once_with("favourites")


def test_clear_favourites_db_error(fav_manager):
    """
    Если db_manager.delete_all_songs выбрасывает OperationalError, clear_favourites вызывает show_critical.
    """
    fav_widget = MagicMock(spec=QListWidget)
    fav_widget.count.return_value = 2
    fav_manager.favourites_widget = fav_widget
    error = OperationalError("Clear error")
    fav_manager.db_manager.delete_all_songs.side_effect = error
    with patch("PyQt5.QtWidgets.QMessageBox.question", return_value=QMessageBox.Yes):
        with patch(
            "controllers.favourites_manager.list_validator.check_list_not_empty",
            return_value=True,
        ):
            with patch.object(
                fav_manager.messanger, "show_critical"
            ) as mock_show_critical:
                fav_manager.clear_favourites()
                mock_show_critical.assert_called_once()
                assert "Clear error" in mock_show_critical.call_args[0][2]


# --- Тесты для add_all_to_favourites ---


def test_add_all_to_favourites_success(fav_manager, mock_parent):
    """
    add_all_to_favourites добавляет все песни из loaded_songs_widget в избранное
    и выводит информационное сообщение с количеством добавленных песен.
    """
    loaded_widget = MagicMock(spec=QListWidget)
    loaded_widget.count.return_value = 3
    item1 = MagicMock(spec=QListWidgetItem)
    item2 = MagicMock(spec=QListWidgetItem)
    item3 = MagicMock(spec=QListWidgetItem)
    item1.data.return_value = "/music/song1.mp3"
    item2.data.return_value = "/music/song2.mp3"
    item3.data.return_value = "/music/song3.mp3"
    loaded_widget.item.side_effect = lambda i: [item1, item2, item3][i]
    mock_parent.ui_provider.get_loaded_songs_widget.return_value = loaded_widget
    fav_manager.loaded_songs_widget = loaded_widget
    fav_manager.db_manager.add_song.side_effect = lambda table, song: None
    with patch.object(fav_manager.messanger, "show_info") as mock_show_info:
        fav_manager.add_all_to_favourites()
        assert fav_manager.db_manager.add_song.call_count == 3
        mock_show_info.assert_called_once()
        args, _ = mock_show_info.call_args
        assert "3" in args[2]


def test_add_all_to_favourites_operational_error(fav_manager, mock_parent):
    """
    Если db_manager.add_song выбрасывает OperationalError, add_all_to_favourites вызывает show_critical.
    """
    loaded_widget = MagicMock(spec=QListWidget)
    loaded_widget.count.return_value = 1
    item = MagicMock(spec=QListWidgetItem)
    item.data.return_value = "/music/song1.mp3"
    loaded_widget.item.return_value = item
    mock_parent.ui_provider.get_loaded_songs_widget.return_value = loaded_widget
    fav_manager.loaded_songs_widget = loaded_widget
    error = OperationalError("Add all error")
    fav_manager.db_manager.add_song.side_effect = error
    with patch(
        "controllers.favourites_manager.list_validator.check_list_not_empty",
        return_value=True,
    ):
        with patch.object(fav_manager.messanger, "show_critical") as mock_show_critical:
            fav_manager.add_all_to_favourites()
            mock_show_critical.assert_called_once()
            assert "Add all error" in mock_show_critical.call_args[0][2]


def test_add_all_to_favourites_integrity_issues(fav_manager, mock_parent):
    """
    Если для некоторых песен возникает IntegrityError, они пропускаются,
    а show_info вызывается с количеством успешно добавленных песен.
    """
    loaded_widget = MagicMock(spec=QListWidget)
    loaded_widget.count.return_value = 3
    item1 = MagicMock(spec=QListWidgetItem)
    item2 = MagicMock(spec=QListWidgetItem)
    item3 = MagicMock(spec=QListWidgetItem)
    item1.data.return_value = "/music/song1.mp3"
    item2.data.return_value = "/music/song2.mp3"
    item3.data.return_value = "/music/song3.mp3"
    loaded_widget.item.side_effect = lambda i: [item1, item2, item3][i]
    mock_parent.ui_provider.get_loaded_songs_widget.return_value = loaded_widget
    fav_manager.loaded_songs_widget = loaded_widget

    def add_song_side_effect(table, song):
        if song == "/music/song1.mp3":
            return
        raise IntegrityError("Already exists")

    fav_manager.db_manager.add_song.side_effect = add_song_side_effect

    with patch.object(fav_manager.messanger, "show_info") as mock_show_info:
        fav_manager.add_all_to_favourites()
        assert fav_manager.db_manager.add_song.call_count == 3
        mock_show_info.assert_called_once()
        args, _ = mock_show_info.call_args
        assert "1" in args[2]


# --- Тест для _get_current_playing_song ---


def test_get_current_playing_song(fav_manager, mock_parent):
    """
    Проверяет, что _get_current_playing_song возвращает корректный путь к текущей песне.
    """
    media_player = MagicMock()
    media = MagicMock()
    media.canonicalUrl.return_value.toLocalFile.return_value = "current_song.mp3"
    media_player.media.return_value = media
    mock_parent.music_controller.media_player.return_value = media_player
    result = fav_manager._get_current_playing_song()
    assert result == "current_song.mp3"

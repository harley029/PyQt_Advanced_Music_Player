# pylint: disable=redefined-outer-name
from unittest.mock import MagicMock, patch
import pytest
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QMessageBox

# Импортируем тестируемый класс и объект list_validator
from controllers.favourites_manager import FavouritesManager
from utils.list_validator import list_validator


# Фикстура для создания мока ui_provider, который возвращает моки для виджетов favourites и loaded_songs
@pytest.fixture
def mock_ui_provider():
    ui_provider = MagicMock()
    favourites_widget = MagicMock(spec=QListWidget)
    loaded_songs_widget = MagicMock(spec=QListWidget)
    ui_provider.get_favourites_widget.return_value = favourites_widget
    ui_provider.get_loaded_songs_widget.return_value = loaded_songs_widget
    return ui_provider, favourites_widget, loaded_songs_widget


# Фикстура для создания мока родительского объекта
@pytest.fixture
def mock_parent(mock_ui_provider):
    ui_provider, favourites_widget, loaded_songs_widget = mock_ui_provider
    parent = MagicMock()
    # Настраиваем методы БД
    parent.db_manager = MagicMock()
    parent.db_manager.fetch_all_songs.return_value = []
    parent.db_manager.add_song = MagicMock()
    parent.db_manager.delete_song = MagicMock()
    parent.db_manager.delete_all_songs = MagicMock()
    parent.ui_provider = ui_provider
    # Мок list_widget_provider с методом get_currently_selected_song
    list_widget_provider = MagicMock()
    list_widget_provider.get_currently_selected_song.return_value = "song.mp3"
    parent.list_widget_provider = list_widget_provider
    # Мок музыкального контроллера с media_player()
    music_controller = MagicMock()
    media_player = MagicMock()
    media = MagicMock()
    media.canonicalUrl.return_value.toLocalFile.return_value = "song.mp3"
    media_player.media.return_value = media
    music_controller.media_player.return_value = media_player
    parent.music_controller = music_controller
    parent.loaded_songs_listWidget = loaded_songs_widget
    parent.favourites_listWidget = favourites_widget
    parent.current_playlist = None
    return parent


# Фикстура для создания экземпляра FavouritesManager
@pytest.fixture
def fav_manager(mock_parent):
    return FavouritesManager(mock_parent)


# Фикстура для патчинга методов MessageManager внутри FavouritesManager,
# чтобы не отображались реальные диалоговые окна
@pytest.fixture(autouse=True)
def patch_message_manager():
    with patch(
        "controllers.favourites_manager.MessageManager.show_warning"
    ) as show_warning, patch(
        "controllers.favourites_manager.MessageManager.show_critical"
    ) as show_critical, patch(
        "controllers.favourites_manager.MessageManager.show_info"
    ) as show_info, patch(
        "controllers.favourites_manager.MessageManager.show_question",
        return_value=QMessageBox.Yes,
    ):
        yield {
            "show_warning": show_warning,
            "show_critical": show_critical,
            "show_info": show_info,
        }


# ---------------------- Тесты для FavouritesManager ------------------------


def test_load_favourites_success(fav_manager):
    """
    Проверяет, что load_favourites очищает favourites_widget и добавляет песни из БД.
    """
    fav_manager.db_manager.fetch_all_songs.return_value = [
        "/music/song1.mp3",
        "/music/song2.mp3",
    ]
    fav_manager.favourites_widget = MagicMock(spec=QListWidget)
    fav_manager.favourites_widget.clear = MagicMock()
    fav_manager.favourites_widget.addItem = MagicMock()

    fav_manager.load_favourites()

    fav_manager.favourites_widget.clear.assert_called_once()
    fav_manager.db_manager.fetch_all_songs.assert_called_once_with("favourites")
    # addItem должен быть вызван два раза (по числу песен)
    assert fav_manager.favourites_widget.addItem.call_count == 2


def test_add_to_favourites_success(fav_manager, mock_parent):
    """
    Тестирует, что add_to_favourites вызывает добавление песни в БД, если песня выбрана.
    """
    loaded_widget = MagicMock(spec=QListWidget)
    loaded_widget.count.return_value = 1
    item = MagicMock(spec=QListWidgetItem)
    item.data.return_value = "song.mp3"
    loaded_widget.currentItem.return_value = item
    mock_parent.ui_provider.get_loaded_songs_widget.return_value = loaded_widget
    fav_manager.loaded_songs_widget = loaded_widget

    fav_manager.add_to_favourites()

    fav_manager.db_manager.add_song.assert_called_once_with("favourites", "song.mp3")


def test_add_to_favourites_no_selection(fav_manager, mock_parent):
    """
    Если текущая песня не выбрана (None), add_to_favourites не вызывает добавление и показывает предупреждение.
    """
    loaded_widget = MagicMock(spec=QListWidget)
    loaded_widget.count.return_value = 1
    loaded_widget.currentItem.return_value = None
    mock_parent.ui_provider.get_loaded_songs_widget.return_value = loaded_widget
    fav_manager.loaded_songs_widget = loaded_widget
    mock_parent.list_widget_provider.get_currently_selected_song.return_value = None

    with patch.object(fav_manager.messanger, "show_warning") as mock_show_warning:
        fav_manager.add_to_favourites()
        fav_manager.db_manager.add_song.assert_not_called()
        mock_show_warning.assert_called_once()


def test_remove_selected_favourite_success(fav_manager, mock_parent):
    """
    Тестирует, что remove_selected_favourite корректно удаляет выбранную песню из UI и БД,
    а также вызывает остановку воспроизведения, если удаляется текущая песня.
    """
    fav_widget = MagicMock(spec=QListWidget)
    item = MagicMock(spec=QListWidgetItem)
    item.data.return_value = "song.mp3"
    fav_widget.count.return_value = 1
    fav_widget.item.side_effect = (
        lambda i: item
    )  # возвращаем один и тот же элемент для любого индекса
    fav_widget.currentRow.return_value = 0
    fav_manager.favourites_widget = fav_widget

    # Патчим _get_current_playing_song, чтобы вернуть "song.mp3"
    with patch.object(
        fav_manager, "_get_current_playing_song", return_value="song.mp3"
    ):
        fav_manager.remove_selected_favourite()

    mock_parent.music_controller.stop_song.assert_called_once()
    fav_manager.db_manager.delete_song.assert_called_once_with("favourites", "song.mp3")
    fav_widget.takeItem.assert_called_once()


def test_remove_selected_favourite_empty_list(fav_manager, mock_parent):
    """
    Если favourites_widget пуст (count == 0), remove_selected_favourite ничего не делает.
    """
    with patch.object(list_validator, "check_list_not_empty", return_value=False):
        fav_widget = MagicMock(spec=QListWidget)
        fav_widget.count.return_value = 0
        fav_manager.favourites_widget = fav_widget
        fav_manager.remove_selected_favourite()
        mock_parent.music_controller.stop_song.assert_not_called()
        fav_manager.db_manager.delete_song.assert_not_called()


def test_remove_selected_favourite_no_selection(fav_manager, mock_parent):
    """
    Если check_item_selected возвращает False (нет выбранного элемента),
    remove_selected_favourite не производит удаление.
    """
    with patch.object(list_validator, "check_item_selected", return_value=False):
        fav_widget = MagicMock(spec=QListWidget)
        fav_widget.count.return_value = 1
        fav_manager.favourites_widget = fav_widget
        fav_manager.remove_selected_favourite()
        mock_parent.music_controller.stop_song.assert_not_called()
        fav_manager.db_manager.delete_song.assert_not_called()


def test_clear_favourites_success(fav_manager, mock_parent):
    """
    Тестирует, что clear_favourites очищает UI и базу данных, если пользователь подтверждает удаление.
    Для того чтобы остановка воспроизведения произошла, в favourites_widget должен быть хотя бы один элемент,
    возвращающий "song.mp3", совпадающую с результатом _get_current_playing_song.
    """
    fav_widget = MagicMock(spec=QListWidget)
    fav_widget.count.return_value = 2
    # Создаём мок-элемент, который возвращает "song.mp3" при вызове data(Qt.UserRole)
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


def test_add_all_to_favourites_success(fav_manager, mock_parent):
    """
    Тестирует, что add_all_to_favourites добавляет все песни из loaded_songs_widget в избранное
    и выводит информационное сообщение с количеством добавленных песен.
    """
    loaded_widget = MagicMock(spec=QListWidget)
    loaded_widget.count.return_value = 3
    # Создаем 3 элемента, возвращающих разные пути
    item1 = MagicMock(spec=QListWidgetItem)
    item2 = MagicMock(spec=QListWidgetItem)
    item3 = MagicMock(spec=QListWidgetItem)
    item1.data.return_value = "/music/song1.mp3"
    item2.data.return_value = "/music/song2.mp3"
    item3.data.return_value = "/music/song3.mp3"
    loaded_widget.item.side_effect = lambda i: [item1, item2, item3][i]
    mock_parent.ui_provider.get_loaded_songs_widget.return_value = loaded_widget
    fav_manager.loaded_songs_widget = loaded_widget

    # Пусть метод add_song базы данных работает корректно
    fav_manager.db_manager.add_song.side_effect = lambda table, song: None

    with patch.object(fav_manager.messanger, "show_info") as mock_show_info:
        fav_manager.add_all_to_favourites()
        # Ожидаем, что add_song будет вызван 3 раза
        assert fav_manager.db_manager.add_song.call_count == 3
        mock_show_info.assert_called_once()
        args, _ = mock_show_info.call_args
        # Проверяем, что в сообщении содержится цифра "3"
        assert "3" in args[2]


def test_get_current_playing_song(fav_manager, mock_parent):
    """
    Тестирует, что _get_current_playing_song возвращает корректный путь к текущей песне.
    """
    media_player = MagicMock()
    media = MagicMock()
    media.canonicalUrl.return_value.toLocalFile.return_value = "current_song.mp3"
    media_player.media.return_value = media
    mock_parent.music_controller.media_player.return_value = media_player

    result = fav_manager._get_current_playing_song()
    assert result == "current_song.mp3"

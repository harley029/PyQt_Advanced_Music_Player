# pylint: disable=redefined-outer-name
from unittest.mock import MagicMock
import pytest

# Предположим, что PlaylistDatabaseManager находится в модуле utils.playlist_database_manager
from interfaces.playlists.playlist_database_manager import PlaylistDatabaseManager


# Фикстура для создания мока для базы данных (IDatabaseManager)
@pytest.fixture
def mock_db_manager():
    db_manager = MagicMock()
    return db_manager


# Фикстура для создания экземпляра PlaylistDatabaseManager с подменённым db_manager
@pytest.fixture
def playlist_db_manager(mock_db_manager):
    return PlaylistDatabaseManager(mock_db_manager)


# Тест для create_playlist, когда плейлист отсутствует в списке
def test_create_playlist_not_existing(playlist_db_manager, mock_db_manager):
    # Настраиваем get_tables, чтобы возвращалась коллекция, не содержащая нужное имя
    mock_db_manager.get_tables.return_value = ["playlist1", "playlist2"]

    playlist_db_manager.create_playlist("new_playlist")

    # Проверяем, что create_table был вызван с "new_playlist"
    mock_db_manager.create_table.assert_called_once_with("new_playlist")


# Тест для create_playlist, когда плейлист уже существует
def test_create_playlist_already_exists(playlist_db_manager, mock_db_manager):
    # Если плейлист уже есть, то метод create_table() не должен вызываться
    mock_db_manager.get_tables.return_value = [
        "playlist1",
        "existing_playlist",
        "playlist2",
    ]

    playlist_db_manager.create_playlist("existing_playlist")

    mock_db_manager.create_table.assert_not_called()


# Тест для delete_playlist
def test_delete_playlist(playlist_db_manager, mock_db_manager):
    playlist_db_manager.delete_playlist("playlist1")
    mock_db_manager.delete_table.assert_called_once_with("playlist1")


# Тест для get_playlists: проверка исключения "favourites"
def test_get_playlists_excludes_favourites(playlist_db_manager, mock_db_manager):
    # Если в базе есть "favourites", он должен быть удалён из результата
    mock_db_manager.get_tables.return_value = ["favourites", "playlist1", "playlist2"]

    playlists = playlist_db_manager.get_playlists()

    assert "favourites" not in playlists
    assert set(playlists) == {"playlist1", "playlist2"}


# Тест для get_playlists, когда "favourites" отсутствует
def test_get_playlists_no_favourites(playlist_db_manager, mock_db_manager):
    mock_db_manager.get_tables.return_value = ["playlist1", "playlist2"]

    playlists = playlist_db_manager.get_playlists()
    assert set(playlists) == {"playlist1", "playlist2"}


# Тест для add_song_to_playlist
def test_add_song_to_playlist(playlist_db_manager, mock_db_manager):
    playlist_db_manager.add_song_to_playlist("playlist1", "song.mp3")
    mock_db_manager.add_song.assert_called_once_with("playlist1", "song.mp3")


# Тест для fetch_all_songs
def test_fetch_all_songs(playlist_db_manager, mock_db_manager):
    expected_songs = ["song1.mp3", "song2.mp3"]
    mock_db_manager.fetch_all_songs.return_value = expected_songs

    songs = playlist_db_manager.fetch_all_songs("playlist1")

    assert songs == expected_songs
    mock_db_manager.fetch_all_songs.assert_called_once_with("playlist1")

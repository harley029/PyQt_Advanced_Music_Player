# pylint: disable=redefined-outer-name
from unittest.mock import MagicMock
import pytest

from interfaces.playlists.playlist_database_manager import PlaylistDatabaseManager


@pytest.fixture
def mock_db_manager():
    """
    Fixture that creates a mock database manager.

    Returns:
        MagicMock: A mock object simulating a database manager.
    """
    db_manager = MagicMock()
    return db_manager


@pytest.fixture
def playlist_db_manager(mock_db_manager):
    """
    Fixture that creates a PlaylistDatabaseManager with a mock database manager.

    Args:
        mock_db_manager: The mock database manager fixture.

    Returns:
        PlaylistDatabaseManager: An instance of PlaylistDatabaseManager for testing.
    """
    return PlaylistDatabaseManager(mock_db_manager)


def test_create_playlist_not_existing(playlist_db_manager, mock_db_manager):
    """
    Test creating a playlist that doesn't already exist.

    Verifies that create_table is called once with the correct playlist name
    when the playlist doesn't already exist in the database.

    Args:
        playlist_db_manager: The PlaylistDatabaseManager fixture.
        mock_db_manager: The mock database manager fixture.
    """
    mock_db_manager.get_tables.return_value = ["playlist1", "playlist2"]
    playlist_db_manager.create_playlist("new_playlist")
    mock_db_manager.create_table.assert_called_once_with("new_playlist")


def test_create_playlist_already_exists(playlist_db_manager, mock_db_manager):
    """
    Test creating a playlist that already exists.

    Verifies that create_table is not called when attempting to create
    a playlist that already exists in the database.

    Args:
        playlist_db_manager: The PlaylistDatabaseManager fixture.
        mock_db_manager: The mock database manager fixture.
    """
    mock_db_manager.get_tables.return_value = [
        "playlist1",
        "existing_playlist",
        "playlist2",
    ]
    playlist_db_manager.create_playlist("existing_playlist")
    mock_db_manager.create_table.assert_not_called()


def test_delete_playlist(playlist_db_manager, mock_db_manager):
    """
    Test deleting a playlist.

    Verifies that delete_table is called once with the correct playlist name.

    Args:
        playlist_db_manager: The PlaylistDatabaseManager fixture.
        mock_db_manager: The mock database manager fixture.
    """
    playlist_db_manager.delete_playlist("playlist1")
    mock_db_manager.delete_table.assert_called_once_with("playlist1")


def test_get_playlists_excludes_favourites(playlist_db_manager, mock_db_manager):
    """
    Test that get_playlists excludes the 'favourites' playlist.

    Verifies that the 'favourites' playlist is excluded from the returned list
    of playlists when it exists in the database.

    Args:
        playlist_db_manager: The PlaylistDatabaseManager fixture.
        mock_db_manager: The mock database manager fixture.
    """
    mock_db_manager.get_tables.return_value = ["favourites", "playlist1", "playlist2"]
    playlists = playlist_db_manager.get_playlists()
    assert "favourites" not in playlists
    assert set(playlists) == {"playlist1", "playlist2"}


def test_get_playlists_no_favourites(playlist_db_manager, mock_db_manager):
    """
    Test get_playlists when 'favourites' playlist doesn't exist.

    Verifies that get_playlists returns all playlists when
    the 'favourites' playlist doesn't exist in the database.

    Args:
        playlist_db_manager: The PlaylistDatabaseManager fixture.
        mock_db_manager: The mock database manager fixture.
    """
    mock_db_manager.get_tables.return_value = ["playlist1", "playlist2"]
    playlists = playlist_db_manager.get_playlists()
    assert set(playlists) == {"playlist1", "playlist2"}


def test_add_song_to_playlist(playlist_db_manager, mock_db_manager):
    """
    Test adding a song to a playlist.

    Verifies that add_song is called once with the correct playlist name and song.

    Args:
        playlist_db_manager: The PlaylistDatabaseManager fixture.
        mock_db_manager: The mock database manager fixture.
    """
    playlist_db_manager.add_song_to_playlist("playlist1", "song.mp3")
    mock_db_manager.add_song.assert_called_once_with("playlist1", "song.mp3")


def test_fetch_all_songs(playlist_db_manager, mock_db_manager):
    """
    Test fetching all songs from a playlist.

    Verifies that fetch_all_songs returns the expected list of songs
    and that the method is called with the correct playlist name.

    Args:
        playlist_db_manager: The PlaylistDatabaseManager fixture.
        mock_db_manager: The mock database manager fixture.
    """
    expected_songs = ["song1.mp3", "song2.mp3"]
    mock_db_manager.fetch_all_songs.return_value = expected_songs
    songs = playlist_db_manager.fetch_all_songs("playlist1")
    assert songs == expected_songs
    mock_db_manager.fetch_all_songs.assert_called_once_with("playlist1")

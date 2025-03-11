# pylint: disable=redefined-outer-name
import os
import sqlite3
from unittest.mock import patch, MagicMock

import pytest

from database.db_manager import DatabaseManager, DatabaseException
from database.db_utils import DBUtils


# Test fixtures
@pytest.fixture
def db_manager():
    """Create a test instance of DatabaseManager with in-memory database."""
    manager = DatabaseManager(db_name=":memory:")
    connection = sqlite3.connect(":memory:")
    manager._connect = lambda: connection
    yield manager
    connection.close()


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary directory for database tests."""
    db_dir = tmp_path / "test_dbs"
    db_dir.mkdir()
    return db_dir


# Tests for initialization and directory creation
def test_init_default_values():
    """Test initialization with default values."""
    manager = DatabaseManager()
    assert manager.db_name == "qtbeets_db.db"
    assert os.path.basename(manager.db_dir) == ".dbs"
    assert os.path.join(manager.db_dir, manager.db_name) == manager.db_path


def test_init_custom_values():
    """Test initialization with custom values."""
    manager = DatabaseManager(db_name="custom.db", db_dir="/tmp/custom_dir")
    assert manager.db_name == "custom.db"
    assert manager.db_dir == "/tmp/custom_dir"
    assert manager.db_path == "/tmp/custom_dir/custom.db"


def test_ensure_database_directory(temp_db_path):
    """Test that the database directory is created if it doesn't exist."""
    test_dir = str(temp_db_path / "new_dir")
    manager = DatabaseManager(db_dir=test_dir)
    assert os.path.exists(test_dir)


def test_ensure_database_directory_error():
    """Test handling of directory creation errors."""
    with patch("os.makedirs") as mock_makedirs:
        mock_makedirs.side_effect = OSError("Permission denied")
        with patch("os.path.exists", return_value=False):
            with pytest.raises(OSError):
                DatabaseManager(db_dir="/nonexistent/path")


# Tests for connection handling
def test_connect_success(db_manager):
    """Test successful database connection."""
    # Restore original method for this test
    original_connect = db_manager._connect
    db_manager._connect = DatabaseManager._connect.__get__(db_manager)

    with patch("sqlite3.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        conn = db_manager._connect()
        assert conn == mock_conn
        mock_connect.assert_called_once_with(db_manager.db_path)

    # Restore patched method
    db_manager._connect = original_connect


def test_connect_failure(db_manager):
    """Test handling of connection failures."""
    # Restore original method for this test
    original_connect = db_manager._connect
    db_manager._connect = DatabaseManager._connect.__get__(db_manager)

    with patch("sqlite3.connect") as mock_connect:
        mock_connect.side_effect = sqlite3.Error("Connection error")
        with pytest.raises(sqlite3.Error):
            db_manager._connect()

    # Restore patched method
    db_manager._connect = original_connect


# Tests for SQL injection prevention
def test_table_escaped():
    """Test table name escaping to prevent SQL injection."""
    manager = DatabaseManager()
    assert manager._table_escaped("users") == '"users"'
    # Test with potentially dangerous input
    assert (
        manager._table_escaped("users; DROP TABLE users;")
        == '"users; DROP TABLE users;"'
    )


# Tests for query execution
def test_execute_query_success(db_manager):
    """Test successful query execution."""
    # Create a test table
    db_manager.execute_query("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")

    # Insert data
    db_manager.execute_query("INSERT INTO test (name) VALUES (?)", ("Test Name",))

    # Fetch data
    result = db_manager.execute_query("SELECT * FROM test", fetch=True)
    assert len(result) == 1
    assert result[0][1] == "Test Name"


def test_execute_query_integrity_error(db_manager):
    """Test handling of integrity constraint violations."""
    # Create table with unique constraint
    db_manager.execute_query(
        "CREATE TABLE unique_test (id INTEGER PRIMARY KEY, name TEXT UNIQUE)"
    )

    # Insert data
    db_manager.execute_query(
        "INSERT INTO unique_test (name) VALUES (?)", ("Unique Name",)
    )

    # Try to insert duplicate (should raise IntegrityError)
    with pytest.raises(sqlite3.IntegrityError):
        db_manager.execute_query(
            "INSERT INTO unique_test (name) VALUES (?)", ("Unique Name",)
        )


def test_execute_query_error(db_manager):
    """Test handling of general SQL errors."""
    # Try invalid SQL syntax
    with pytest.raises(DatabaseException):
        db_manager.execute_query("SELECT * FROMM nonexistent_table")


# Tests for song management
def test_add_song(db_manager):
    """Test adding a song to a table."""
    # Create a test table
    db_manager.create_table("playlist")

    # Add a song
    db_manager.add_song("playlist", "/path/to/song.mp3")

    # Verify song was added
    songs = db_manager.fetch_all_songs("playlist")
    assert len(songs) == 1
    assert songs[0] == "/path/to/song.mp3"


def test_add_duplicate_song(db_manager):
    """Test handling of duplicate song entries."""
    # Create a test table
    db_manager.create_table("playlist")

    # Add a song
    db_manager.add_song("playlist", "/path/to/song.mp3")

    # Try to add the same song again (should raise IntegrityError)
    with pytest.raises(sqlite3.IntegrityError):
        db_manager.add_song("playlist", "/path/to/song.mp3")


def test_delete_song(db_manager):
    """Test deleting a song from a table."""
    # Create a test table and add songs
    db_manager.create_table("playlist")
    db_manager.add_song("playlist", "/path/to/song1.mp3")
    db_manager.add_song("playlist", "/path/to/song2.mp3")

    # Delete one song
    db_manager.delete_song("playlist", "/path/to/song1.mp3")

    # Verify deletion
    songs = db_manager.fetch_all_songs("playlist")
    assert len(songs) == 1
    assert songs[0] == "/path/to/song2.mp3"


def test_delete_all_songs(db_manager):
    """Test deleting all songs from a table."""
    # Create a test table and add songs
    db_manager.create_table("playlist")
    db_manager.add_song("playlist", "/path/to/song1.mp3")
    db_manager.add_song("playlist", "/path/to/song2.mp3")

    # Delete all songs
    db_manager.delete_all_songs("playlist")

    # Verify deletion
    songs = db_manager.fetch_all_songs("playlist")
    assert len(songs) == 0


# Tests for table management
def test_create_table(db_manager):
    """Test creating a new table."""
    # Create a table
    db_manager.create_table("new_playlist")

    # Verify table was created
    tables = db_manager.get_tables()
    assert "new_playlist" in tables


def test_create_table_with_custom_columns(db_manager):
    """Test creating a table with custom columns."""
    # Create a table with custom columns
    db_manager.create_table(
        "custom_table", "id INTEGER PRIMARY KEY, title TEXT, artist TEXT"
    )

    # Verify table structure
    result = db_manager.execute_query("PRAGMA table_info(custom_table)", fetch=True)

    columns = [row[1] for row in result]  # Column names are at index 1
    assert "id" in columns
    assert "title" in columns
    assert "artist" in columns


def test_create_table_invalid_name(db_manager):
    """Test handling of invalid table names."""
    with patch.object(DBUtils, "is_valid_table_name", return_value=False):
        with pytest.raises(ValueError):
            db_manager.create_table("invalid;table")


def test_delete_table(db_manager):
    """Test deleting a table."""
    # Create a table
    db_manager.create_table("temp_playlist")

    # Delete the table
    db_manager.delete_table("temp_playlist")

    # Verify table was deleted
    tables = db_manager.get_tables()
    assert "temp_playlist" not in tables


def test_get_tables(db_manager):
    """Test retrieving all tables."""
    # Create multiple tables
    db_manager.create_table("playlist1")
    db_manager.create_table("playlist2")
    db_manager.create_table("playlist3")

    # Get all tables
    tables = db_manager.get_tables()

    # Verify all tables are returned
    assert "playlist1" in tables
    assert "playlist2" in tables
    assert "playlist3" in tables


def test_fetch_all_songs(db_manager):
    """Test retrieving all songs from a table."""
    # Create a table and add songs
    db_manager.create_table("test_playlist")
    songs = ["/path/to/song1.mp3", "/path/to/song2.mp3", "/path/to/song3.mp3"]

    for song in songs:
        db_manager.add_song("test_playlist", song)

    # Fetch all songs
    fetched_songs = db_manager.fetch_all_songs("test_playlist")

    # Verify all songs are returned
    assert set(fetched_songs) == set(songs)
    assert len(fetched_songs) == 3


# Integration tests
def test_full_workflow(db_manager):
    """Integration test for a complete workflow."""
    # 1. Create tables
    db_manager.create_table("favorites")
    db_manager.create_table("recent_plays")

    # 2. Add songs to tables
    favorite_songs = ["/path/to/favorite1.mp3", "/path/to/favorite2.mp3"]
    recent_songs = [
        "/path/to/recent1.mp3",
        "/path/to/recent2.mp3",
        "/path/to/recent3.mp3",
    ]

    for song in favorite_songs:
        db_manager.add_song("favorites", song)

    for song in recent_songs:
        db_manager.add_song("recent_plays", song)

    # 3. Verify songs were added correctly
    assert set(db_manager.fetch_all_songs("favorites")) == set(favorite_songs)
    assert set(db_manager.fetch_all_songs("recent_plays")) == set(recent_songs)

    # 4. Delete a song
    db_manager.delete_song("favorites", "/path/to/favorite1.mp3")
    assert db_manager.fetch_all_songs("favorites") == ["/path/to/favorite2.mp3"]

    # 5. Delete all songs from a table
    db_manager.delete_all_songs("recent_plays")
    assert db_manager.fetch_all_songs("recent_plays") == []

    # 6. Delete a table
    db_manager.delete_table("favorites")
    tables = db_manager.get_tables()
    assert "favorites" not in tables
    assert "recent_plays" in tables

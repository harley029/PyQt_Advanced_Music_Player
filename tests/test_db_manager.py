# pylint: disable=redefined-outer-name
import os
import sqlite3
from unittest.mock import patch, MagicMock

import pytest

from database.db_manager import DatabaseManager, DatabaseException
from database.db_utils import DBUtils


@pytest.fixture
def db_manager():
    """Create a test instance of DatabaseManager with in-memory database.

    Returns:
        DatabaseManager: An instance of DatabaseManager configured with an in-memory SQLite database
        for testing purposes. The connection is closed after the test completes.
    """
    manager = DatabaseManager(db_name=":memory:")
    connection = sqlite3.connect(":memory:")
    manager._connect = lambda: connection
    yield manager
    connection.close()


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary directory for database tests.

    Args:
        tmp_path (Path): Pytest fixture that provides a temporary directory unique to the test invocation.

    Returns:
        Path: A Path object pointing to a newly created temporary directory for database testing.
    """
    db_dir = tmp_path / "test_dbs"
    db_dir.mkdir()
    return db_dir


def test_init_default_values():
    """Test initialization with default values.

    Ensures that DatabaseManager correctly initializes with expected default values
    when no parameters are provided.

    Returns:
        None
    """
    manager = DatabaseManager()
    assert manager.db_name == "qtbeets_db.db"
    assert os.path.basename(manager.db_dir) == ".dbs"
    assert os.path.join(manager.db_dir, manager.db_name) == manager.db_path


def test_init_custom_values():
    """Test initialization with custom values.

    Verifies that the DatabaseManager correctly uses custom values when they are
    provided during initialization.

    Returns:
        None
    """
    manager = DatabaseManager(db_name="some.db", db_dir="/tmp/db_dir")
    assert manager.db_name == "some.db"
    assert manager.db_dir == "/tmp/db_dir"
    assert manager.db_path == "/tmp/db_dir/some.db"


def test_ensure_database_directory(temp_db_path):
    """Test that the database directory is created if it doesn't exist.

    Args:
        temp_db_path (Path): A pytest fixture providing a temporary directory path.

    Returns:
        None

    Verifies that DatabaseManager creates the specified database directory
    if it doesn't already exist.
    """
    test_dir = str(temp_db_path / "new_dir")
    manager = DatabaseManager(db_dir=test_dir)
    assert os.path.exists(test_dir)


def test_ensure_database_directory_error():
    """Test handling of directory creation errors.

    Returns:
        None

    Validates that DatabaseManager correctly propagates OSError exceptions
    when it fails to create the database directory due to permission issues.
    """
    with patch("os.makedirs") as mock_makedirs:
        mock_makedirs.side_effect = OSError("Permission denied")
        with patch("os.path.exists", return_value=False):
            with pytest.raises(OSError):
                DatabaseManager(db_dir="/nonexistent/path")


def test_connect_success(db_manager):
    """Test successful database connection.

    Args:
        db_manager (DatabaseManager): Fixture providing a DatabaseManager instance.

    Returns:
        None

    Verifies that the _connect method successfully establishes a connection
    to the database and returns a valid connection object.
    """
    # Restore original method for this test
    original_connect = db_manager._connect
    # pylint: disable=no-value-for-parameter
    db_manager._connect = DatabaseManager._connect.__get__(db_manager)

    with patch("sqlite3.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        conn = db_manager._connect()
        assert conn == mock_conn
        mock_connect.assert_called_once_with(db_manager.db_path)

    db_manager._connect = original_connect


def test_connect_failure(db_manager):
    """Test handling of connection failures.

    Args:
        db_manager (DatabaseManager): Fixture providing a DatabaseManager instance.

    Returns:
        None

    Validates that the _connect method properly propagates sqlite3.Error
    exceptions when the connection to the database fails.
    """
    original_connect = db_manager._connect
    # pylint: disable=no-value-for-parameter
    db_manager._connect = DatabaseManager._connect.__get__(db_manager)

    with patch("sqlite3.connect") as mock_connect:
        mock_connect.side_effect = sqlite3.Error("Connection error")
        with pytest.raises(sqlite3.Error):
            db_manager._connect()

    db_manager._connect = original_connect


def test_table_escaped():
    """Test table name escaping to prevent SQL injection.

    Returns:
        None

    Verifies that the _table_escaped method correctly escapes table names
    to prevent SQL injection attacks by adding double quotes around table names.
    """
    manager = DatabaseManager()
    assert manager._table_escaped("users") == '"users"'
    assert (
        manager._table_escaped("users; DROP TABLE users;")
        == '"users; DROP TABLE users;"'
    )


def test_execute_query_success(db_manager):
    """Test successful query execution.

    Args:
        db_manager (DatabaseManager): Fixture providing a DatabaseManager instance.

    Returns:
        None

    Confirms that the execute_query method can successfully create tables,
    insert data, and retrieve results when queries are valid.
    """
    db_manager.execute_query("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    db_manager.execute_query("INSERT INTO test (name) VALUES (?)", ("Test Name",))
    result = db_manager.execute_query("SELECT * FROM test", fetch=True)
    assert len(result) == 1
    assert result[0][1] == "Test Name"


def test_execute_query_integrity_error(db_manager):
    """Test handling of integrity constraint violations.

    Args:
        db_manager (DatabaseManager): Fixture providing a DatabaseManager instance.

    Returns:
        None

    Verifies that the execute_query method properly propagates sqlite3.IntegrityError
    when a query violates integrity constraints, such as unique constraints.
    """
    db_manager.execute_query(
        "CREATE TABLE unique_test (id INTEGER PRIMARY KEY, name TEXT UNIQUE)"
    )
    db_manager.execute_query(
        "INSERT INTO unique_test (name) VALUES (?)", ("Unique Name",)
    )
    with pytest.raises(sqlite3.IntegrityError):
        db_manager.execute_query(
            "INSERT INTO unique_test (name) VALUES (?)", ("Unique Name",)
        )


def test_execute_query_error(db_manager):
    """Test handling of general SQL errors.

    Args:
        db_manager (DatabaseManager): Fixture providing a DatabaseManager instance.

    Returns:
        None

    Confirms that the execute_query method properly raises DatabaseException
    when an invalid SQL query is executed.
    """
    with pytest.raises(DatabaseException):
        db_manager.execute_query("SELECT * FROMM nonexistent_table")


def test_add_song(db_manager):
    """Test adding a song to a table.

    Args:
        db_manager (DatabaseManager): Fixture providing a DatabaseManager instance.

    Returns:
        None

    Validates that the add_song method successfully adds a song path to a specified table
    and that the song can be retrieved using fetch_all_songs.
    """
    db_manager.create_table("playlist")
    db_manager.add_song("playlist", "/path/to/song.mp3")
    songs = db_manager.fetch_all_songs("playlist")
    assert len(songs) == 1
    assert songs[0] == "/path/to/song.mp3"


def test_add_duplicate_song(db_manager):
    """Test handling of duplicate song entries.

    Args:
        db_manager (DatabaseManager): Fixture providing a DatabaseManager instance.

    Returns:
        None

    Verifies that the add_song method raises sqlite3.IntegrityError when attempting
    to add a duplicate song to a table, enforcing unique constraints.
    """
    db_manager.create_table("playlist")
    db_manager.add_song("playlist", "/path/to/song.mp3")
    with pytest.raises(sqlite3.IntegrityError):
        db_manager.add_song("playlist", "/path/to/song.mp3")


def test_delete_song(db_manager):
    """Test deleting a song from a table.

    Args:
        db_manager (DatabaseManager): Fixture providing a DatabaseManager instance.

    Returns:
        None

    Confirms that the delete_song method successfully removes a specified song
    from a table while leaving other songs intact.
    """
    db_manager.create_table("playlist")
    db_manager.add_song("playlist", "/path/to/song1.mp3")
    db_manager.add_song("playlist", "/path/to/song2.mp3")
    db_manager.delete_song("playlist", "/path/to/song1.mp3")
    songs = db_manager.fetch_all_songs("playlist")
    assert len(songs) == 1
    assert songs[0] == "/path/to/song2.mp3"


def test_delete_all_songs(db_manager):
    """Test deleting all songs from a table.

    Args:
        db_manager (DatabaseManager): Fixture providing a DatabaseManager instance.

    Returns:
        None

    Verifies that the delete_all_songs method properly removes all songs
    from a specified table, leaving the table empty but intact.
    """
    db_manager.create_table("playlist")
    db_manager.add_song("playlist", "/path/to/song1.mp3")
    db_manager.add_song("playlist", "/path/to/song2.mp3")
    db_manager.delete_all_songs("playlist")
    songs = db_manager.fetch_all_songs("playlist")
    assert len(songs) == 0


def test_create_table(db_manager):
    """Test creating a new table.

    Args:
        db_manager (DatabaseManager): Fixture providing a DatabaseManager instance.

    Returns:
        None

    Validates that the create_table method successfully creates a new table
    in the database and that the table appears in the list of tables.
    """
    db_manager.create_table("new_playlist")
    tables = db_manager.get_tables()
    assert "new_playlist" in tables


def test_create_table_with_custom_columns(db_manager):
    """Test creating a table with custom columns.

    Args:
        db_manager (DatabaseManager): Fixture providing a DatabaseManager instance.

    Returns:
        None

    Confirms that the create_table method correctly creates a table with custom columns
    when a column definition string is provided.
    """
    db_manager.create_table(
        "custom_table", "id INTEGER PRIMARY KEY, title TEXT, artist TEXT"
    )
    result = db_manager.execute_query("PRAGMA table_info(custom_table)", fetch=True)
    columns = [row[1] for row in result]  # Column names are at index 1
    assert "id" in columns
    assert "title" in columns
    assert "artist" in columns


def test_create_table_invalid_name(db_manager):
    """Test handling of invalid table names.

    Args:
        db_manager (DatabaseManager): Fixture providing a DatabaseManager instance.

    Returns:
        None

    Verifies that the create_table method raises ValueError when attempting
    to create a table with an invalid name that could potentially be used for SQL injection.
    """
    with patch.object(DBUtils, "is_valid_table_name", return_value=False):
        with pytest.raises(ValueError):
            db_manager.create_table("invalid;table")


def test_delete_table(db_manager):
    """Test deleting a table.

    Args:
        db_manager (DatabaseManager): Fixture providing a DatabaseManager instance.

    Returns:
        None

    Confirms that the delete_table method successfully removes a specified table
    from the database and that it no longer appears in the list of tables.
    """
    db_manager.create_table("temp_playlist")
    db_manager.delete_table("temp_playlist")
    tables = db_manager.get_tables()
    assert "temp_playlist" not in tables


def test_get_tables(db_manager):
    """Test retrieving all tables.

    Args:
        db_manager (DatabaseManager): Fixture providing a DatabaseManager instance.

    Returns:
        None

    Validates that the get_tables method correctly returns a list of all tables
    in the database after multiple tables have been created.
    """
    db_manager.create_table("playlist1")
    db_manager.create_table("playlist2")
    db_manager.create_table("playlist3")
    tables = db_manager.get_tables()
    assert "playlist1" in tables
    assert "playlist2" in tables
    assert "playlist3" in tables


def test_fetch_all_songs(db_manager):
    """Test retrieving all songs from a table.

    Args:
        db_manager (DatabaseManager): Fixture providing a DatabaseManager instance.

    Returns:
        None

    Confirms that the fetch_all_songs method properly retrieves all songs
    from a specified table after multiple songs have been added.
    """
    db_manager.create_table("test_playlist")
    songs = ["/path/to/song1.mp3", "/path/to/song2.mp3", "/path/to/song3.mp3"]
    for song in songs:
        db_manager.add_song("test_playlist", song)
    fetched_songs = db_manager.fetch_all_songs("test_playlist")
    assert set(fetched_songs) == set(songs)
    assert len(fetched_songs) == 3


def test_full_workflow(db_manager):
    """Integration test for a complete workflow.

    Args:
        db_manager (DatabaseManager): Fixture providing a DatabaseManager instance.

    Returns:
        None

    Performs an end-to-end test of the DatabaseManager functionality, including:
    - Creating multiple tables
    - Adding songs to different tables
    - Verifying song retrieval
    - Deleting individual songs
    - Deleting all songs from a table
    - Deleting tables
    - Verifying the state of the database after each operation

    This test ensures that all components work together correctly in a realistic usage scenario.
    """
    db_manager.create_table("favorites")
    db_manager.create_table("recent_plays")
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
    assert set(db_manager.fetch_all_songs("favorites")) == set(favorite_songs)
    assert set(db_manager.fetch_all_songs("recent_plays")) == set(recent_songs)
    db_manager.delete_song("favorites", "/path/to/favorite1.mp3")
    assert db_manager.fetch_all_songs("favorites") == ["/path/to/favorite2.mp3"]
    db_manager.delete_all_songs("recent_plays")
    assert db_manager.fetch_all_songs("recent_plays") == []
    db_manager.delete_table("favorites")
    tables = db_manager.get_tables()
    assert "favorites" not in tables
    assert "recent_plays" in tables

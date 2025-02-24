import os
import sqlite3
import logging
from typing import List, Tuple, Optional

from database.db_utils import DBUtils
from interfaces.interfaces import IDatabaseManager

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class DatabaseException(Exception):
    """Custom exception for database operation errors."""


class DatabaseManager(IDatabaseManager):
    """
    Concrete implementation of IDatabaseManager interface for SQLite.

    Implements operations for connection, query execution, and data manipulation
    operations including adding, deleting, and retrieving data.
    """

    def __init__(self, db_name: str = "qtbeets_db.db", db_dir: Optional[str] = None):
        """
        Initialize the database manager.

        Parameters:
            db_name: Database file name
            db_dir: Directory for storing the database.
                   If None, uses current directory with '.dbs' subdirectory
        """
        self.db_dir: str = db_dir or os.path.join(os.getcwd(), ".dbs")
        self.db_path: str = os.path.join(self.db_dir, db_name)
        self._ensure_database_directory()
        logging.debug("Database path set to: %s", self.db_path)

    def _ensure_database_directory(self) -> None:
        """
        Check if database directory exists and create it if necessary.

        Raises:
            OSError: If directory creation fails
        """
        if not os.path.exists(self.db_dir):
            try:
                os.makedirs(self.db_dir)
                logging.info("Created database directory at: %s", self.db_dir)
            except OSError as e:
                logging.critical("Failed to create database directory: %s", e)
                raise

    def _connect(self) -> sqlite3.Connection:
        """
        Create and return a database connection.

        Returns:
            sqlite3.Connection object

        Raises:
            Exception: If connection fails
        """
        try:
            conn = sqlite3.connect(self.db_path)
            logging.debug("Database connection established.")
            return conn
        except sqlite3.Error as e:
            logging.critical("Database connection failed: %s", e)
            raise

    def _table_escaped(self, table: str) -> str:
        """
        Escape table name to prevent SQL injection attacks.

        Parameters:
            table: Table name to be escaped

        Returns:
            Escaped table name, e.g. "table"
        """
        return f'"{table}"'

    def execute_query(
        self, query: str, params: Tuple = (), fetch: bool = False
    ) -> List[Tuple]:
        """
        Execute an SQL query on the database.

        Parameters:
            query: SQL query string
            params: Tuple of parameters for the query
            fetch: If True, returns query results

        Returns:
            List of tuples containing query results if fetch=True, empty list otherwise

        Raises:
            DatabaseException: If query execution fails
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                if fetch:
                    result = cursor.fetchall()
                    logging.info(
                        "Executed SELECT query: %s | Params: %s", query, params
                    )
                    return result
                logging.info("Executed query: %s | Params: %s", query, params)
                return []
        except sqlite3.IntegrityError as e:
            logging.warning(
                "Integrity constraint violation: %s | Query: %s | Params: %s",
                e,
                query,
                params,
            )
            raise
        except sqlite3.Error as e:
            logging.exception(
                "Database error: %s | Query: %s | Params: %s", e, query, params
            )
            raise DatabaseException(e) from e

    def add_song(self, table: str, song: str) -> None:
        """
        Add a song to the specified table.

        Parameters:
            table: Table name
            song: Song path or identifier
        """
        query = f"INSERT INTO {self._table_escaped(table)} (song) VALUES (?)"
        logging.debug("Adding song: %s to table: %s", song, table)
        self.execute_query(query, (song,))

    def delete_song(self, table: str, song: str) -> None:
        """
        Delete a song from the specified table.

        Parameters:
            table: Table name
            song: Song path or identifier
        """
        query = f"DELETE FROM {self._table_escaped(table)} WHERE song = ?"
        logging.debug("Deleting song: %s from table: %s", song, table)
        self.execute_query(query, (song,))

    def delete_all_songs(self, table: str) -> None:
        """
        Delete all records (songs) from the specified table.

        Parameters:
            table: Table name
        """
        query = f"DELETE FROM {self._table_escaped(table)}"
        logging.debug("Deleting all songs from table: %s", table)
        self.execute_query(query)

    def create_table(self, table_name: str, columns: str = "song TEXT UNIQUE") -> None:
        """
        Create a table in the database if it doesn't exist.

        Parameters:
            table_name: Name of the table
            columns: String describing table columns

        Raises:
            ValueError: If table name is invalid
        """
        if not DBUtils.is_valid_table_name(table_name):
            logging.error("Attempt to create table with invalid name: %s", table_name)
            raise ValueError("Invalid table name!")
        query = f"CREATE TABLE IF NOT EXISTS {self._table_escaped(table_name)} ({columns})"
        logging.debug("Creating table: %s with columns: %s", table_name, columns)
        self.execute_query(query)

    def delete_table(self, table: str) -> None:
        """
        Delete a table from the database.

        Parameters:
            table: Table name
        """
        table_escaped = f'"{table}"'
        query = f"DROP TABLE IF EXISTS {table_escaped}"
        logging.debug("Dropping table: %s", table)
        self.execute_query(query)

    def get_tables(self) -> List[str]:
        """
        Get a list of all tables in the database.

        Returns:
            List of table names
        """
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = self.execute_query(query, fetch=True)
        table_names = [table[0] for table in tables]
        logging.debug("Retrieved tables: %s", table_names)
        return table_names

    def fetch_all_songs(self, table: str) -> List[str]:
        """
        Retrieve all songs from the specified table.

        Parameters:
            table: Table name

        Returns:
            List of songs
        """
        query = f"SELECT song FROM {table}"
        songs = self.execute_query(query, fetch=True)
        song_list = [song[0] for song in songs]
        logging.debug("Fetched songs from table %s: %s", table, song_list)
        return song_list

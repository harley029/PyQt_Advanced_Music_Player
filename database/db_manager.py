import os
import sqlite3
import logging
import sys
from typing import List, Tuple, Any, Optional

from database.db_utils import DBUtils
from interfaces.interfaces import IDatabaseManager


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Отключаем вывод в консоль
# sys.stdout = open(os.devnull, "w")
# sys.stderr = open(os.devnull, "w")
# # Отключаем ошибки, чтобы они не писались в консоль
# sys.excepthook = lambda exc_type, exc_value, traceback: None

class DatabaseException(Exception):
    """Пользовательское исключение для ошибок работы с базой данных."""
    pass


class DatabaseManager(IDatabaseManager):
    """
    Конкретная реализация интерфейса IDatabaseManager для SQLite.

    Этот класс реализует основные операции с базой данных, такие как подключение, выполнение запросов,
    добавление, удаление и выборка данных. Реализация основана на SQLite.
    """

    def __init__(self, db_name: str = "qtbeets_db.db", db_dir: Optional[str] = None):
        """
        Инициализирует менеджер базы данных.

        :param db_name: Имя файла базы данных.
        :param db_dir: Директория для хранения базы данных. Если None, используется текущая директория с подпапкой ".dbs".
        """
        self.db_dir: str = db_dir or os.path.join(os.getcwd(), ".dbs")
        self.db_path: str = os.path.join(self.db_dir, db_name)
        self._ensure_database_directory()
        logging.debug(f"Database path set to: {self.db_path}")

    def _ensure_database_directory(self) -> None:
        """
        Проверяет существование директории для базы данных и создаёт её при необходимости.

        :raises OSError: Если не удалось создать директорию.
        """
        if not os.path.exists(self.db_dir):
            try:
                os.makedirs(self.db_dir)
                logging.info(f"Created database directory at: {self.db_dir}")
            except OSError as e:
                logging.critical(f"Failed to create database directory: {e}")
                raise

    def _connect(self) -> sqlite3.Connection:
        """
        Создаёт и возвращает соединение с базой данных.

        :return: Объект sqlite3.Connection.
        :raises Exception: Если не удалось установить соединение.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            logging.debug("Database connection established.")
            return conn
        except sqlite3.Error as e:
            logging.critical(f"Database connection failed: {e}")
            raise

    def execute_query(
        self, query: str, params: Tuple = (), fetch: bool = False
    ) -> List[Tuple]:
        """
        Выполняет SQL-запрос к базе данных.

        :param query: SQL-запрос.
        :param params: Кортеж параметров для запроса.
        :param fetch: Если True, возвращает результат запроса.
        :return: Список кортежей с результатами запроса, если fetch=True, иначе пустой список.
        :raises Exception: При ошибке выполнения запроса.
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                if fetch:
                    result = cursor.fetchall()
                    logging.info(f"Executed SELECT query: {query} | Params: {params}")
                    return result
                else:
                    logging.info(f"Executed query: {query} | Params: {params}")
                    return []
        except sqlite3.IntegrityError:
            logging.warning(
                f"Integrity constraint violation: {query} | Params: {params}"
            )
            raise
        except sqlite3.Error as e:
            logging.error(f"Database error: {e} | Query: {query} | Params: {params}")
            raise DatabaseException(e)

    def add_song(self, table: str, song: str) -> None:
        """
        Добавляет песню в указанную таблицу.

        :param table: Имя таблицы.
        :param song: Путь или идентификатор песни.
        """
        table_escaped = f'"{table}"'
        query = f"INSERT INTO {table_escaped} (song) VALUES (?)"
        self.execute_query(query, (song,))

    def delete_song(self, table: str, song: str) -> None:
        """
        Удаляет песню из указанной таблицы.

        :param table: Имя таблицы.
        :param song: Путь или идентификатор песни.
        """
        table_escaped = f'"{table}"'
        query = f"DELETE FROM {table_escaped} WHERE song = ?"
        self.execute_query(query, (song,))

    def delete_all_songs(self, table: str) -> None:
        """
        Удаляет все записи (песни) из указанной таблицы.

        :param table: Имя таблицы.
        """
        table_escaped = f'"{table}"'
        query = f"DELETE FROM {table_escaped}"
        self.execute_query(query)

    def create_table(self, table_name: str, columns: str = "song TEXT UNIQUE") -> None:
        """
        Создаёт таблицу в базе данных, если она ещё не существует.

        :param table_name: Имя таблицы.
        :param columns: Строка, описывающая столбцы таблицы.
        :raises ValueError: Если имя таблицы недопустимо.
        """
        if not DBUtils.is_valid_table_name(table_name):
            raise ValueError("Invalid table name!")
        table_escaped = f'"{table_name}"'
        query = f"CREATE TABLE IF NOT EXISTS {table_escaped} ({columns})"
        self.execute_query(query)

    def delete_table(self, table: str) -> None:
        """
        Удаляет таблицу из базы данных.

        :param table: Имя таблицы.
        """
        table_escaped = f'"{table}"'
        query = f"DROP TABLE IF EXISTS {table_escaped}"
        self.execute_query(query)

    def get_tables(self) -> List[str]:
        """
        Возвращает список всех таблиц в базе данных.

        :return: Список имен таблиц.
        """
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = self.execute_query(query, fetch=True)
        table_names = [table[0] for table in tables]
        return table_names

    def fetch_all_songs(self, table: str) -> List[str]:
        """
        Извлекает все песни из указанной таблицы.

        :param table: Имя таблицы.
        :return: Список песен.
        """
        query = f"SELECT song FROM {table}"
        songs = self.execute_query(query, fetch=True)
        song_list = [song[0] for song in songs]
        return song_list

from abc import ABC, abstractmethod
from typing import List, Tuple, Any


from PyQt5.QtWidgets import QListWidget
from PyQt5.QtMultimedia import QMediaPlayer


class ICommand(ABC):
    """
    Интерфейс команды. Все команды должны реализовывать метод execute().
    """

    @abstractmethod
    def execute(self):
        """
        Выполняет действие команды.
        """
        pass


class IPlaylistManager(ABC):
    """
    Интерфейс менеджера плейлистов.

    Определяет контракт для загрузки, создания, удаления плейлистов и управления UI.
    """

    @abstractmethod
    def load_playlists_into_widget(self) -> None:
        """
        Загружает список плейлистов в соответствующий виджет UI.
        """
        pass

    @abstractmethod
    def load_playlist_into_widget(self, parent) -> None:
        """
        Загружает выбранный плейлист в виджет песен.

        :param parent: Родительский виджет, содержащий списки плейлистов и песен.
        """
        pass

    @abstractmethod
    def create_playlist(self, parent) -> str:
        """
        Создаёт новый плейлист через диалог ввода и обновляет UI.

        :param parent: Родительский виджет.
        :return: Имя созданного плейлиста или None, если операция отменена.
        """
        pass

    @abstractmethod
    def remove_playlist(self, parent) -> None:
        """
        Удаляет выбранный плейлист и обновляет UI.

        :param parent: Родительский виджет.
        """
        pass

    @abstractmethod
    def remove_all_playlists(self, parent) -> None:
        """
        Удаляет все плейлисты и обновляет UI.

        :param parent: Родительский виджет.
        """
        pass

    @abstractmethod
    def check_list_not_empty(
        self, list_widget: QListWidget, message: str = "No songs in the list!"
    ) -> bool:
        """
        Проверяет, что переданный виджет не пуст.

        :param list_widget: Виджет со списком элементов.
        :param message: Сообщение об ошибке, если список пуст.
        :return: True, если список не пуст, иначе False.
        """
        pass

    @abstractmethod
    def add_song_to_playlist(self, parent) -> None:
        """
        Добавляет выбранную песню в выбранный плейлист.

        :param parent: Родительский виджет.
        """
        pass

    @abstractmethod
    def add_all_to_playlist(self, parent) -> None:
        """
        Добавляет все песни из списка в выбранный плейлист.

        :param parent: Родительский виджет.
        """
        pass


class IPlaylistDatabaseManager(ABC):
    """Интерфейс для работы с базой данных плейлистов."""

    @abstractmethod
    def create_playlist(self, name: str):
        """Создаёт новый плейлист в базе."""
        pass

    @abstractmethod
    def delete_playlist(self, name: str):
        """Удаляет плейлист из базы."""
        pass

    @abstractmethod
    def add_song_to_playlist(self, playlist: str, song: str):
        """Добавляет песню в плейлист."""
        pass

    @abstractmethod
    def remove_song_from_playlist(self, playlist: str, song: str):
        """Удаляет песню из плейлиста."""
        pass

    @abstractmethod
    def get_playlists(self) -> List[str]:
        """Возвращает список всех плейлистов."""
        pass


class IPlaylistUIManager(ABC):
    """Интерфейс для управления UI плейлистов."""

    @abstractmethod
    def load_playlists(self):
        """Загружает плейлисты в UI."""
        pass

    @abstractmethod
    def load_playlist(self, playlist: str, list_widget: QListWidget):
        """Загружает плейлист в UI."""
        pass

    @abstractmethod
    def refresh_playlists(self):
        """Обновляет UI при изменении плейлиста."""
        pass

    @abstractmethod
    def check_list_not_empty(self, list_widget: QListWidget, message: str) -> bool:
        """Проверяет, что переданный виджет не пуст."""
        pass
    @abstractmethod
    def select_playlist(self, parent_widget: QListWidget):
        """Возвращает выбранный плейлист."""
        pass


class INavigationStrategy(ABC):
    """
    Интерфейс навигационной стратегии для выбора следующей или предыдущей песни.
    """

    @abstractmethod
    def get_next_index(self, current_index: int, count: int) -> int:
        """
        Вычисляет индекс следующей песни.

        :param current_index: текущий индекс песни
        :param count: общее количество песен
        :return: индекс следующей песни
        """
        pass

    @abstractmethod
    def get_previous_index(self, current_index: int, count: int) -> int:
        """
        Вычисляет индекс предыдущей песни.

        :param current_index: текущий индекс песни
        :param count: общее количество песен
        :return: индекс предыдущей песни
        """
        pass


class IDatabaseManager(ABC):
    """
    Интерфейс для работы с базой данных.

    Этот интерфейс определяет набор методов для подключения к базе данных,
    выполнения SQL-запросов, а также операций по добавлению, удалению и выборке данных.

    Использование интерфейса позволяет реализовывать разные стратегии доступа к данным
    (например, SQLite, PostgreSQL, MySQL) без изменения бизнес-логики приложения.
    """

    @abstractmethod
    def _connect(self) -> Any:
        """
        Создаёт и возвращает соединение с базой данных.

        :return: Объект соединения с базой данных (например, sqlite3.Connection).
        """
        pass

    @abstractmethod
    def execute_query(
        self, query: str, params: Tuple = (), fetch: bool = False
    ) -> List[Tuple]:
        """
        Выполняет SQL-запрос к базе данных.

        :param query: SQL-запрос в виде строки.
        :param params: Кортеж параметров для параметризованного запроса (по умолчанию пустой кортеж).
        :param fetch: Если True, возвращает результаты запроса, иначе возвращает пустой список.
        :return: Список кортежей с результатами, если fetch=True, иначе пустой список.
        """
        pass

    @abstractmethod
    def add_song(self, table: str, song: str) -> None:
        """
        Добавляет песню в указанную таблицу базы данных.

        :param table: Имя таблицы.
        :param song: Путь или идентификатор песни.
        """
        pass

    @abstractmethod
    def delete_song(self, table: str, song: str) -> None:
        """
        Удаляет песню из указанной таблицы базы данных.

        :param table: Имя таблицы.
        :param song: Путь или идентификатор песни.
        """
        pass

    @abstractmethod
    def delete_all_songs(self, table: str) -> None:
        """
        Удаляет все записи (песни) из указанной таблицы базы данных.

        :param table: Имя таблицы.
        """
        pass

    @abstractmethod
    def create_table(self, table_name: str, columns: str = "song TEXT UNIQUE") -> None:
        """
        Создаёт таблицу в базе данных, если она ещё не существует.

        :param table_name: Имя таблицы.
        :param columns: Строка с описанием столбцов (по умолчанию используется один столбец "song" с уникальными значениями).
        """
        pass

    @abstractmethod
    def delete_table(self, table: str) -> None:
        """
        Удаляет таблицу из базы данных, если она существует.

        :param table: Имя таблицы.
        """
        pass

    @abstractmethod
    def get_tables(self) -> List[str]:
        """
        Возвращает список всех таблиц в базе данных.

        :return: Список имен таблиц.
        """
        pass

    @abstractmethod
    def fetch_all_songs(self, table: str) -> List[str]:
        """
        Извлекает все песни из указанной таблицы базы данных.

        :param table: Имя таблицы.
        :return: Список песен (например, путей к файлам).
        """
        pass


class IMusicPlayerController(ABC):


    @abstractmethod
    def set_volume(self, volume: int):
        pass

    @abstractmethod
    def current_volume(self) -> int:
        pass

    @abstractmethod
    def play_song(self, song_path: str):
        pass

    @abstractmethod
    def stop_song(self):
        pass

    @abstractmethod
    def pause_song(self):
        pass

    @abstractmethod
    def resume_song(self):
        pass

    @abstractmethod
    def is_playing(self) -> bool:
        pass

    @abstractmethod
    def is_paused(self) -> bool:
        pass

    @abstractmethod
    def set_looped(self, looped: bool):
        pass

    @abstractmethod
    def set_shuffled(self, shuffled: bool):
        pass
    
    @abstractmethod
    def media_player(self) -> QMediaPlayer:
        pass

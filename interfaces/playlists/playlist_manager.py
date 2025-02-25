from sqlite3 import IntegrityError, DatabaseError
from typing import Optional

from PyQt5.QtWidgets import QListWidget, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt

from interfaces.interfaces import IPlaylistManager
from interfaces.playlists.playlist_database_manager import PlaylistDatabaseManager
from interfaces.playlists.playlist_ui_manager import PlaylistUIManager
from utils import messages as msg
from utils.message_manager import messanger
from utils.list_validator import list_validator


class PlaylistError(Exception):
    """Custom exception for playlist-related errors"""

    # pass


class PlaylistManager(IPlaylistManager):
    """
    Менеджер плейлистов, объединяющий работу с базой данных и UI.

    Использует PlaylistDatabaseManager для операций с базой данных
    и PlaylistUIManager для обновления интерфейса.
    """
    def __init__(self, db_manager, playlist_widget: QListWidget):
        """
        :param db_manager: Объект, реализующий IDatabaseManager, для работы с базой.
        :param playlist_widget: Виджет, в который будут загружаться плейлисты.
        """
        self.db_manager = PlaylistDatabaseManager(db_manager)
        self.ui_manager = PlaylistUIManager(playlist_widget, self.db_manager)

    def load_playlists_into_widget(self):
        """Загружает плейлисты в UI."""
        self.ui_manager.load_playlists()

    def load_playlist_into_widget(self, parent):
        """
        Загружает выбранный плейлист в виджет песен. Если ничего не выбрано,
        выводит сообщение о необходимости выбора.

        :param parent: Родительский виджет, содержащий списки плейлистов и песен.
        """
        try:
            if parent.playlists_listWidget.count() == 0:
                messanger.show_info(parent, msg.TTL_INF, msg.MSG_NO_LSTS)
                return
            current_selection = parent.playlists_listWidget.selectedItems()
            if not current_selection:
                messanger.show_info(parent, msg.TTL_WRN, msg.MSG_NO_LST_SEL)
                return
            current_selection = parent.playlists_listWidget.currentRow()
            item = parent.playlists_listWidget.item(current_selection)
            if not item:
                return

            current_playlist = item.text().strip()
            parent.current_playlist = current_playlist
            self.ui_manager.load_playlist(current_playlist, parent.loaded_songs_listWidget)
            parent.switch_to_songs_tab()
        except DatabaseError as e:
            messanger.show_critical(
                parent, msg.TTL_ERR, f"Database error while loading playlist: {e}"
            )
        except PlaylistError as e:
            messanger.show_critical(parent, msg.TTL_ERR, f"Playlist error: {e}")

    def create_playlist(self, parent) -> Optional[str]:
        """
        Создаёт новый плейлист через диалог ввода и обновляет UI.

        :param parent: Родительский виджет.
        :return: Имя созданного плейлиста или None.
        """
        try:
            existing = self.db_manager.get_playlists()
            playlist_name, ok = QInputDialog.getText(
                parent, "New Playlist", "Enter the name of the new playlist:"
            )

            if not ok or not playlist_name.strip():
                return None

            if playlist_name not in existing:
                self.db_manager.create_playlist(playlist_name)
            else:
                caution = messanger.show_question(
                    parent,
                    msg.TTL_LST_REPL,
                    f'A playlist with name "{playlist_name}" already exists.\nDo you want to replace it?',
                )
                if caution == QMessageBox.Yes:
                    self.db_manager.delete_playlist(playlist_name)
                    self.db_manager.create_playlist(playlist_name)
                else:
                    return None

            self.ui_manager.load_playlists()
        except ValueError as e:
            messanger.show_critical(parent, msg.TTL_ERR, f"Invalid playlist name: {e}")
        except DatabaseError as e:
            messanger.show_critical(
                parent, msg.TTL_ERR, f"Database error while creating playlist: {e}"
            )

        return playlist_name

    def remove_playlist(self, parent):
        """
        Удаляет выбранный плейлист и обновляет UI.

        :param parent: Родительский виджет.
        """
        try:
            if parent.playlists_listWidget.count() == 0:
                messanger.show_info(
                    parent, msg.TTL_INF, "There are no playlists to be deleted"
                )
                return
            current_selection = parent.playlists_listWidget.selectedItems()
            if not current_selection:
                messanger.show_info(parent, msg.TTL_WRN, msg.MSG_NO_LST_SEL)
                return
            current_selection = parent.playlists_listWidget.currentRow()
            item = parent.playlists_listWidget.item(current_selection)
            if not item:
                return

            playlist_name = item.text().strip()
            confirm = messanger.show_question(
                parent,
                msg.TTL_LST_DEL,
                f"{msg.MSG_LST_DEL_QUEST} '{playlist_name}'?"
            )
            if confirm != QMessageBox.Yes:
                return

            if parent.current_playlist == playlist_name:
                parent.music_controller.stop_song()
                parent.ui_updater.clear_song_info()
                parent.current_playlist = None
            self.db_manager.delete_playlist(playlist_name)
            parent.playlists_listWidget.takeItem(current_selection)
            if parent.playlists_listWidget.count() > 0:
                new_selection = current_selection % parent.playlists_listWidget.count()
                parent.playlists_listWidget.setCurrentRow(new_selection)
        except DatabaseError as e:
            messanger.show_critical(
                parent, msg.TTL_ERR, f"Database error while removing playlist: {e}"
            )
        except PlaylistError as e:
            messanger.show_critical(parent, msg.TTL_ERR, f"Playlist error: {e}")

    def remove_all_playlists(self, parent):
        """
        Удаляет все плейлисты и обновляет UI.

        :param parent: Родительский виджет.
        """
        try:
            if not list_validator.check_list_not_empty(
                parent.playlists_listWidget, "There are no playlists to be deleted"
            ):
                return
            confirm = messanger.show_question(
                parent,
                msg.TTL_LST_DEL,
                msg.MSG_LST_DEL_QUEST
            )
            if confirm != QMessageBox.Yes:
                return

            if parent.current_playlist and parent.current_playlist.lower() != "favourites":
                parent.music_controller.stop_song()
                parent.ui_updater.clear_song_info()
                parent.current_playlist = None

            playlists = self.db_manager.get_playlists()
            for playlist in playlists:
                self.db_manager.delete_playlist(playlist)
            parent.playlists_listWidget.clear()
            # messanger.show_info(parent, msg.TTL_OK, msg.MSG_LST_DEL_OK)
        except DatabaseError as e:
            messanger.show_critical(
                parent, msg.TTL_ERR, f"Database error while removing playlists: {e}"
            )
        except PlaylistError as e:
            messanger.show_critical(parent, msg.TTL_ERR, f"Playlist error: {e}")

    def add_song_to_playlist(self, parent):
        """
        Добавляет выбранную песню в выбранный плейлист.

        :param parent: Родительский виджет.
        """
        try:
            if not list_validator.check_list_not_empty(
                parent.loaded_songs_listWidget, "No songs in the list!"
            ):
                return
            if not list_validator.check_item_selected(parent.loaded_songs_listWidget, parent):
                return

            item = parent.loaded_songs_listWidget.currentItem()
            if not item:
                messanger.show_info(parent, msg.TTL_ATT, msg.MSG_NO_SONG_SEL)
                return
            current_song = item.data(Qt.UserRole)

            playlist, ok = self.ui_manager.select_playlist(parent)
            if not ok:  # Пользователь нажал "Отмена"
                return
            if playlist == "--Click to Select--":
                messanger.show_info(parent, msg.TTL_ADD_TO_LST, msg.MSG_NO_LST_SEL)
                return

            self.db_manager.add_song_to_playlist(playlist, current_song)
        except IntegrityError:
            messanger.show_warning(
                parent, msg.TTL_WRN, f"{msg.MSG_SONG_EXIST} {playlist}."
            )
        except DatabaseError as e:
            messanger.show_critical(
                parent, msg.TTL_ERR, f"Database error while adding song: {e}"
            )
        except PlaylistError as e:
            messanger.show_critical(parent, msg.TTL_ERR, f"Playlist error: {e}")

    def add_all_to_playlist(self, parent) -> None:
        """
        Adds all songs from the list to the selected playlist.

        Args:
            parent: Parent widget containing the song list.
        """
        try:
            if not list_validator.check_list_not_empty(
                parent.loaded_songs_listWidget, "List of songs is empty!"
            ):
                return

            playlist, ok = self.ui_manager.select_playlist(parent)
            if not ok:
                return
            if playlist == "--Click to Select--":
                messanger.show_info(parent, msg.TTL_ADD_TO_LST, msg.MSG_NO_LST_SEL)
                return

            added_count = 0
            for i in range(parent.loaded_songs_listWidget.count()):
                item = parent.loaded_songs_listWidget.item(i)
                current_song = item.data(Qt.UserRole)
                if not current_song:
                    continue
                try:
                    self.db_manager.add_song_to_playlist(playlist, current_song)
                    added_count += 1
                except IntegrityError:
                    # Skip if song already exists in playlist
                    continue
                except (DatabaseError) as e:
                    raise PlaylistError(f"Failed to add song to playlist: {e}") from e
            messanger.show_info(
                parent, msg.TTL_OK, f"{added_count} {msg.CTX_ADD_ALL_TO_LST}"
            )

        except PlaylistError as e:
            messanger.show_critical(parent, msg.TTL_ERR, str(e))
        except DatabaseError as e:
            messanger.show_critical(parent, msg.TTL_ERR, f"Database error while adding songs: {e}")
        except ValueError as e:
            messanger.show_critical(parent, msg.TTL_ERR, f"Invalid data format: {e}")

    # def check_list_not_empty(self, list_widget: QListWidget, message: str = "No songs in the list!") -> bool:
    #     result = self.ui_manager.check_list_not_empty(list_widget, message)
    #     return result

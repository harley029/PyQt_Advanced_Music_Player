from sqlite3 import IntegrityError, DatabaseError
from typing import Optional

from PyQt5.QtWidgets import QListWidget, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt

from interfaces.interfaces import IPlaylistManager
from interfaces.playlists.playlist_database_manager import PlaylistDatabaseManager
from interfaces.playlists.playlist_ui_manager import PlaylistUIManager
from utils import messages as msg
from utils.message_manager import MessageManager
from utils.list_validator import list_validator
from utils import messages as msg


class PlaylistError(Exception):
    """Custom exception for playlist-related errors"""


class PlaylistManager(IPlaylistManager):
    """
    Playlist manager that combines database operations and UI management.

    Uses PlaylistDatabaseManager for database operations
    and PlaylistUIManager for updating the user interface.
    """
    def __init__(self, db_manager, playlist_widget: QListWidget):
        """
        Initialize the PlaylistManager.

        :param db_manager: Object implementing IDatabaseManager interface for database operations.
        :param playlist_widget: Widget where playlists will be loaded.
        """
        self.db_manager = PlaylistDatabaseManager(db_manager)
        self.ui_manager = PlaylistUIManager(playlist_widget, self.db_manager)
        self.list_widget = playlist_widget
        self.messanger = MessageManager()

    def load_playlists_into_widget(self):
        """
        Load playlists into the UI widget.
        """
        self.ui_manager.load_playlists()

    def load_playlist_into_widget(self, parent):
        """
        Load the selected playlist into the songs widget.
        If nothing is selected, displays a message about the need to make a selection.

        :param parent: Parent widget containing playlist and song lists.
        """
        try:
            if not list_validator.check_list_not_empty(self.list_widget, msg.MSG_NO_LSTS):
                return
            if not list_validator.check_item_selected(self.list_widget, parent, message=msg.MSG_NO_LST_SEL):
                return
            current_selection = self.list_widget.currentRow()
            item = self.list_widget.item(current_selection)
            if not item:
                return

            current_playlist = item.text().strip()
            parent.current_playlist = current_playlist
            self.ui_manager.load_playlist(current_playlist, parent.loaded_songs_listWidget)
            parent.switch_to_songs_tab()
        except DatabaseError as e:
            self.messanger.show_critical(
                parent, msg.TTL_ERR, f"{msg.DB_LST_LOAD_ERROR} {e}"
            )
        except PlaylistError as e:
            self.messanger.show_critical(
                parent, msg.TTL_ERR, f"{msg.MSG_LST_LOAD_ERR} {e}"
            )

    def create_playlist(self, parent) -> Optional[str]:
        """
        Create a new playlist through an input dialog and update the UI.

        :param parent: Parent widget.
        :return: Name of the created playlist or None.
        """
        playlist_name = None
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
                caution = self.messanger.show_question(
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
            self.messanger.show_critical(
                parent, msg.TTL_ERR, f"{msg.MSG_LST_NAME_ERROR} {e}"
            )
        except DatabaseError as e:
            self.messanger.show_critical(
                parent, msg.TTL_ERR, f"{msg.DB_LST_NEW_ERROR} {e}"
            )

        return playlist_name

    def remove_playlist(self, parent):
        """
        Remove the selected playlist and update the UI.

        :param parent: Parent widget.
        """
        try:
            if not list_validator.check_list_not_empty(
                self.list_widget, msg.MSG_NO_LST_TO_DEL
            ):
                return
            if not list_validator.check_item_selected(self.list_widget, parent, message=msg.MSG_NO_LST_SEL):
                return
            current_selection = self.list_widget.currentRow()
            item = self.list_widget.item(current_selection)
            if not item:
                return

            playlist_name = item.text().strip()
            confirm = self.messanger.show_question(
                parent, msg.TTL_LST_DEL, f"{msg.MSG_LST_DEL_QUEST} '{playlist_name}'?"
            )
            if confirm != QMessageBox.Yes:
                return

            if parent.current_playlist == playlist_name:
                parent.music_controller.stop_song()
                parent.ui_updater.clear_song_info()
                parent.current_playlist = None
            self.db_manager.delete_playlist(playlist_name)
            self.list_widget.takeItem(current_selection)
            if self.list_widget.count() > 0:
                new_selection = current_selection % self.list_widget.count()
                self.list_widget.setCurrentRow(new_selection)
        except DatabaseError as e:
            self.messanger.show_critical(
                parent, msg.TTL_ERR, f"{msg.DB_LST_DEL_ERROR} {e}"
            )
        except PlaylistError as e:
            self.messanger.show_critical(parent, msg.TTL_ERR, f"{msg.MSG_LST_ERR} {e}")

    def remove_all_playlists(self, parent):
        """
        Remove all playlists and update the UI.

        :param parent: Parent widget.
        """
        try:
            if not list_validator.check_list_not_empty(
                parent.playlists_listWidget, msg.MSG_NO_LST_TO_DEL
            ):
                return
            confirm = self.messanger.show_question(
                parent, msg.TTL_LST_DEL, msg.MSG_LST_DEL_QUEST
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
            # self.messanger.show_info(parent, msg.TTL_OK, msg.MSG_LST_DEL_OK)
        except DatabaseError as e:
            self.messanger.show_critical(
                parent, msg.TTL_ERR, f"{msg.DB_LST_DEL_ERROR} {e}"
            )
        except PlaylistError as e:
            self.messanger.show_critical(parent, msg.TTL_ERR, f"{msg.MSG_LST_ERR} {e}")

    def add_song_to_playlist(self, parent):
        """
        Add the selected song to the selected playlist.

        :param parent: Parent widget.
        """
        try:
            if not list_validator.check_list_not_empty(
                parent.loaded_songs_listWidget, msg.MSG_LST_EMPTY
            ):
                return
            if not list_validator.check_item_selected(parent.loaded_songs_listWidget, parent):
                return

            item = parent.loaded_songs_listWidget.currentItem()
            if not item:
                self.messanger.show_info(parent, msg.TTL_ATT, msg.MSG_NO_SONG_SEL)
                return
            current_song = item.data(Qt.UserRole)

            playlist, ok = self.ui_manager.select_playlist(parent)
            if not ok:
                return
            if playlist == "--Click to Select--":
                self.messanger.show_info(parent, msg.TTL_ADD_TO_LST, msg.MSG_NO_LST_SEL)
                return

            self.db_manager.add_song_to_playlist(playlist, current_song)
        except IntegrityError:
            self.messanger.show_warning(
                parent, msg.TTL_WRN, f"{msg.MSG_SONG_EXIST} {playlist}."
            )
        except DatabaseError as e:
            self.messanger.show_critical(
                parent, msg.TTL_ERR, f"{msg.DB_SONG_ADD_ERROR} {e}"
            )
        except PlaylistError as e:
            self.messanger.show_critical(parent, msg.TTL_ERR, f"{msg.MSG_LST_ERR} {e}")

    def add_all_to_playlist(self, parent) -> None:
        """
        Add all songs from the list to the selected playlist.

        :param parent: Parent widget containing the song list.
        """
        try:
            if not list_validator.check_list_not_empty(
                parent.loaded_songs_listWidget, msg.MSG_LST_EMPTY
            ):
                return

            playlist, ok = self.ui_manager.select_playlist(parent)
            if not ok:
                return
            if playlist == "--Click to Select--":
                self.messanger.show_info(parent, msg.TTL_ADD_TO_LST, msg.MSG_NO_LST_SEL)
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
                    raise PlaylistError(f"{msg.MSG_ADD_TO_LST_ERR} {e}") from e
            self.messanger.show_info(
                parent, msg.TTL_OK, f"{added_count} {msg.CTX_ADD_ALL_TO_LST}"
            )

        except PlaylistError as e:
            self.messanger.show_critical(parent, msg.TTL_ERR, str(e))
        except DatabaseError as e:
            self.messanger.show_critical(
                parent, msg.TTL_ERR, f"{msg.DB_SONG_ADD_ERROR} {e}"
            )
        except ValueError as e:
            self.messanger.show_critical(
                parent, msg.TTL_ERR, f"{msg.MSG_DATA_FORMAT_ERROR} {e}"
            )

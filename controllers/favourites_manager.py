from sqlite3 import IntegrityError, OperationalError
import os
from typing import Optional

from PyQt5.QtWidgets import QMessageBox, QListWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from utils import messages as msg
from utils.message_manager import MessageManager
from utils.list_validator import list_validator


class FavouritesManager:
    """
    A class to manage favorite songs in a music player application.

    This class handles all operations related to the favorites list including
    adding, removing, and displaying favorite songs. It interfaces with a database
    to persist the favorites data and manages the UI representation of the favorites list.

    Attributes:
        parent: The parent widget containing this manager
        db_manager: Database manager instance for handling song storage
        list_widget: QListWidget displaying the favorites list
        loaded_songs_listWidget: QListWidget displaying currently loaded songs
    """

    def __init__(self, parent):
        """
        Initialize the Favourites Manager controller.

        Sets up the FavouritesManager instance.
        """
        self.parent = parent
        self.db_manager = parent.db_manager
        self.ui_provider = parent.ui_provider
        self.favourites_widget = self.ui_provider.get_favourites_widget()
        self.loaded_songs_widget = self.ui_provider.get_loaded_songs_widget()
        self.list_widget_provider = parent.list_widget_provider
        self.messanger = MessageManager()

    def _get_current_playing_song(self) -> Optional[str]:
        """
        Get the file path of the currently playing song.

        Returns:
            str: The file path of the currently playing song, or None if no song is playing
        """
        current_media = self.parent.music_controller.media_player().media()
        return current_media.canonicalUrl().toLocalFile() if current_media else None

    def _remove_song_from_ui_and_db(self, song_path: str) -> None:
        """
        Remove a song from both the UI list and database.

        Args:
            song_path (str): The file path of the song to remove

        Note:
            Removes the first occurrence of the song in the favorites list
            and deletes it from the database
        """
        for i in range(self.favourites_widget.count()):
            item = self.favourites_widget.item(i)
            if item and item.data(Qt.UserRole) == song_path:
                self.favourites_widget.takeItem(i)
                self.db_manager.delete_song("favourites", song_path)
                break

    def load_favourites(self) -> None:
        """
        Load all favorite songs from the database and display them in the UI.

        Clears the current favorites list and populates it with songs from the database.
        Each song is displayed with a like icon and the filename.

        Raises:
            OperationalError: If there's an error accessing the database
            OSError: If there's an error accessing the file system
        """
        try:
            self.favourites_widget.clear()
            songs = self.db_manager.fetch_all_songs("favourites")
            for song in songs:
                item = QListWidgetItem(
                    QIcon(":/img/utils/images/like.png"), os.path.basename(song)
                )
                item.setData(Qt.UserRole, song)
                self.favourites_widget.addItem(item)
        except (OperationalError, OSError) as e:
            self.messanger.show_critical(
                self.parent, msg.TTL_ERR, f"{msg.MSG_FAV_ERR_LOAD} {str(e)}"
            )

    def add_to_favourites(self) -> None:
        """
        Add the currently selected song from the loaded songs list to favorites.

        Checks if a song is selected and adds it to both the UI and database.
        Shows appropriate message boxes for various conditions and errors.

        Raises:
            IntegrityError: If the song already exists in favorites
            OperationalError: If there's an error accessing the database
        """
        try:
            if not list_validator.check_list_not_empty(self.loaded_songs_widget):
                return
            if not list_validator.check_item_selected(self.loaded_songs_widget, self.parent):
                return
            current_song = self.list_widget_provider.get_currently_selected_song()
            if current_song is None:
                self.messanger.show_warning(
                    self.parent, msg.TTL_WRN, msg.MSG_NO_SONG_SEL
                )
                return
            self.db_manager.add_song("favourites", current_song)
        except IntegrityError:
            self.messanger.show_warning(self.parent, msg.TTL_WRN, msg.MSG_FAV_EXIST)
        except OperationalError as e:
            self.messanger.show_critical(
                self.parent, msg.TTL_ERR, f"{msg.MSG_FAV_ERR_ADD} {str(e)}"
            )

    def remove_selected_favourite(self) -> None:
        """
        Remove the currently selected song from the favorites list.

        If the removed song is currently playing, stops playback and starts
        playing the next song in the list. Updates the selection to maintain
        UI consistency.

        Raises:
            OperationalError: If there's an error accessing the database
            OSError: If there's an error accessing the file system
        """
        try:
            if not list_validator.check_list_not_empty(self.favourites_widget):
                return
            if not list_validator.check_item_selected(self.favourites_widget, self.parent):
                return
            current_selection = self.favourites_widget.currentRow()
            current_song = self.list_widget_provider.get_currently_selected_song()
            current_song_path = self._get_current_playing_song()
            was_playing = current_song_path == current_song

            if was_playing:
                self.parent.music_controller.stop_song()

            self._remove_song_from_ui_and_db(current_song)

            if self.favourites_widget.count() > 0:
                new_selection = min(current_selection, self.favourites_widget.count() - 1)
                self.favourites_widget.setCurrentRow(new_selection)

            if was_playing and self.favourites_widget.count() > 0:
                next_song = self.favourites_widget.item(new_selection).data(Qt.UserRole)
                self.parent.music_controller.play_song(next_song)

        except (OperationalError, OSError) as e:
            self.messanger.show_critical(
                self.parent, msg.TTL_ERR, f"{msg.MSG_SONG_DEL_ERR} {str(e)}"
            )

    def clear_favourites(self) -> None:
        """
        Remove all songs from the favorites list.

        Prompts for confirmation before clearing. If the currently playing
        song is in the favorites list, stops playback. Clears both the UI
        list and database.

        Raises:
            OperationalError: If there's an error accessing the database
        """
        try:
            if not list_validator.check_list_not_empty(self.favourites_widget):
                return
            confirm = self.messanger.show_question(
                self.parent, msg.TTL_FAV_QUEST, msg.MSG_FAV_QUEST
            )
            if confirm != QMessageBox.Yes:
                return

            current_song_path = self._get_current_playing_song()
            is_playing = any(
                self.favourites_widget.item(i).data(Qt.UserRole) == current_song_path
                for i in range(self.favourites_widget.count())
            )

            if is_playing:
                self.parent.music_controller.stop_song()

            self.favourites_widget.clear()
            self.db_manager.delete_all_songs("favourites")

        except OperationalError as e:
            self.messanger.show_critical(
                self.parent, msg.TTL_ERR, f"{msg.MSG_FAF_CLEAR_ERR} {str(e)}"
            )

    def add_all_to_favourites(self) -> None:
        """
        Add all songs from the loaded songs list to favorites.

        Attempts to add each song, skipping those that already exist in favorites.
        Shows a message with the number of successfully added songs.

        Raises:
            OperationalError: If there's an error accessing the database
        """
        try:
            if not list_validator.check_list_not_empty(self.loaded_songs_widget):
                return

            added_count = 0
            for i in range(self.loaded_songs_widget.count()):
                item = self.loaded_songs_widget.item(i)
                song_path = item.data(Qt.UserRole)
                if not song_path:
                    continue
                try:
                    self.db_manager.add_song("favourites", song_path)
                    added_count += 1
                except IntegrityError:
                    pass
            self.messanger.show_info(
                self.parent, msg.TTL_OK, f"{added_count} {msg.MSG_FAV_ADDED}"
            )
        except OperationalError as e:
            self.messanger.show_critical(
                self.parent, msg.TTL_ERR, f"{msg.MSG_FAV_ERR_ADD_ALL} {str(e)}"
            )

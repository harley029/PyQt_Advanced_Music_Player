from sqlite3 import IntegrityError
import os

from PyQt5.QtWidgets import QListWidget, QMessageBox, QListWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


class FavouritesManager:

    def __init__(self, parent):
        self.parent = parent
        self.db_manager = parent.db_manager
        self.list_widget = parent.favourites_listWidget
        self.loaded_songs_listWidget = parent.loaded_songs_listWidget

    def _get_current_playing_song(self):
        current_media = self.parent.music_controller.media_player().media()
        return current_media.canonicalUrl().toLocalFile() if current_media else None

    def _check_list_not_empty(self, list_widget:QListWidget):
        if list_widget.count() == 0:
            QMessageBox.information(self.parent, "Attention!", "List is empty!")
            return False
        return True

    def _remove_song_from_ui_and_db(self, song_path):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item and item.data(Qt.UserRole) == song_path:
                self.list_widget.takeItem(i)
                self.db_manager.delete_song("favourites", song_path)
                break

    def load_favourites(self):
        try:
            self.list_widget.clear()
            songs = self.db_manager.fetch_all_songs("favourites")
            for song in songs:
                item = QListWidgetItem(
                    QIcon(":/img/utils/images/like.png"), os.path.basename(song)
                )
                item.setData(Qt.UserRole, song)
                self.list_widget.addItem(item)
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Error loading favourites: {e}")

    def add_to_favourites(self):
        try:
            if not self._check_list_not_empty(self.loaded_songs_listWidget):
                return
            item = self.parent.loaded_songs_listWidget.currentItem()
            if not item:
                QMessageBox.information(self.parent, "Attention", "No song selected!")
                return
            current_song = item.data(Qt.UserRole)
            self.db_manager.add_song("favourites", current_song)
        except IntegrityError:
            QMessageBox.warning(self.parent, "Warning", "Song already in favourites.")
        except Exception as e:
            QMessageBox.critical(
                self.parent, "Error", f"Error adding to favourites: {e}"
            )

    def remove_selected_favourite(self):
        try:
            if not self._check_list_not_empty(self.parent.favourites_listWidget):
                return

            current_selection = self.list_widget.currentRow()
            item = self.list_widget.currentItem()
            if not item:
                QMessageBox.information(self.parent, "Warning", "No song selected!")
                return

            current_song = item.data(Qt.UserRole)
            current_song_path = self._get_current_playing_song()
            was_playing = (current_song_path == current_song)

            if was_playing:
                self.parent.music_controller.stop_song()

            self._remove_song_from_ui_and_db(current_song)

            if self.list_widget.count() > 0:
                new_selection = min(current_selection, self.list_widget.count() - 1)
                self.list_widget.setCurrentRow(new_selection)

            if was_playing:
                next_song = self.list_widget.item(new_selection).data(Qt.UserRole)
                self.parent.music_controller.play_song(next_song)

        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Error removing song: {e}")

    def clear_favourites(self):
        try:
            if not self._check_list_not_empty(self.parent.favourites_listWidget):
                return
            confirm = QMessageBox.question(
                self.parent,
                "Remove all favourites",
                "Are you sure you want to remove all songs from favourites?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if confirm != QMessageBox.Yes:
                return

            current_song_path = self._get_current_playing_song()
            is_playing = any(
                self.list_widget.item(i).data(Qt.UserRole) == current_song_path
                for i in range(self.list_widget.count())
            )

            if is_playing:
                self.parent.music_controller.stop_song()

            self.list_widget.clear()
            self.db_manager.delete_all_songs("favourites")

        except Exception as e:
            QMessageBox.critical(
                self.parent, "Error", f"Error clearing favourites: {e}"
            )

    def add_all_to_favourites(self):
        try:
            if not self._check_list_not_empty(self.parent.loaded_songs_listWidget):
                return

            added_count = 0
            for i in range(self.parent.loaded_songs_listWidget.count()):
                item = self.parent.loaded_songs_listWidget.item(i)
                song_path = item.data(Qt.UserRole)
                if not song_path:
                    continue
                try:
                    self.db_manager.add_song("favourites", song_path)
                    added_count += 1
                except IntegrityError:
                    pass  # Пропускаем уже существующие песни

            QMessageBox.information(
                self.parent, "Success", f"{added_count} songs added to Favourites."
            )

        except Exception as e:
            QMessageBox.critical(
                self.parent, "Error", f"Error adding all songs to Favourites: {e}"
            )

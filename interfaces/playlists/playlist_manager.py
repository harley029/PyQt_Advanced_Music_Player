from sqlite3 import IntegrityError

from PyQt5.QtWidgets import QListWidget, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt

from interfaces.interfaces import IPlaylistManager
from interfaces.playlists.playlist_database_manager import PlaylistDatabaseManager
from interfaces.playlists.playlist_ui_manager import PlaylistUIManager


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
                QMessageBox.information(parent, "Attention!", "List of playlists is empty!")
                return
            current_selection = parent.playlists_listWidget.selectedItems()
            if not current_selection:
                QMessageBox.information(parent, "Warning", "No playlist selected!")
                return
            current_selection = parent.playlists_listWidget.currentRow()
            item = parent.playlists_listWidget.item(current_selection)
            if not item:
                return

            current_playlist = item.text().strip()
            parent.current_playlist = current_playlist
            self.ui_manager.load_playlist(current_playlist, parent.loaded_songs_listWidget)
            parent.switch_to_songs_tab()
        except Exception as e:
            QMessageBox.critical(parent, "Error", f"Error loading playlist: {e}")

    def create_playlist(self, parent):
        """
        Создаёт новый плейлист через диалог ввода и обновляет UI.

        :param parent: Родительский виджет.
        :return: Имя созданного плейлиста или None.
        """
        try:
            existing = self.db_manager.get_playlists()
            playlist_name, ok = QInputDialog.getText(parent, "New Playlist", "Enter the name of the new playlist:")
            if not ok or not playlist_name.strip():
                return None

            if playlist_name not in existing:
                self.db_manager.create_playlist(playlist_name)
            else:
                caution = QMessageBox.question(
                    parent,
                    "Replace Playlist",
                    f'A playlist with name "{playlist_name}" already exists.\nDo you want to replace it?',
                    QMessageBox.Yes | QMessageBox.Cancel,
                    QMessageBox.Cancel,
                )
                if caution == QMessageBox.Yes:
                    self.db_manager.delete_playlist(playlist_name)
                    self.db_manager.create_playlist(playlist_name)
                else:
                    return None

            self.ui_manager.load_playlists()
        except ValueError as e:
            QMessageBox.critical(parent, "Error", f"Имя плейлиста может содержать буквы латинского и украинского алфавиотов, а также знаки подчеркивания, тире, восклицательные знаки и пробелы")
        return playlist_name

    def remove_playlist(self, parent):
        """
        Удаляет выбранный плейлист и обновляет UI.

        :param parent: Родительский виджет.
        """
        try:
            if parent.playlists_listWidget.count() == 0:
                QMessageBox.information(
                    parent, "Attention!", "List of playlists is empty!"
                )
                return
            current_selection = parent.playlists_listWidget.selectedItems()
            if not current_selection:
                QMessageBox.information(parent, "Warning", "No playlist selected!")
                return
            current_selection = parent.playlists_listWidget.currentRow()
            item = parent.playlists_listWidget.item(current_selection)
            if not item:
                return

            playlist_name = item.text().strip()
            confirm = QMessageBox.question(
                parent,
                "Delete Playlist",
                f"Are you sure you want to delete playlist '{playlist_name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
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
            QMessageBox.information(
                parent, "Success", f"Playlist '{playlist_name}' has been deleted."
            )
        except Exception as e:
            QMessageBox.critical(parent, "Error", f"Error removing playlist: {e}")

    def remove_all_playlists(self, parent):
        """
        Удаляет все плейлисты и обновляет UI.

        :param parent: Родительский виджет.
        """
        try:
            if parent.playlists_listWidget.count() == 0:
                QMessageBox.information(parent, "Attention!", "List of playlists is empty!")
                return
            confirm = QMessageBox.question(
                parent,
                "Delete Playlist",
                f"Are you sure you want to delete all playlists?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
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
            QMessageBox.information(parent, "Success", f"Playlists have been deleted.")
        except Exception as e:
            QMessageBox.critical(parent, "Error", f"Error removing playlist: {e}")

    def check_list_not_empty(self, list_widget: QListWidget, message: str = "No songs in the list!") -> bool:
        result = self.ui_manager.check_list_not_empty(list_widget, message)
        return result

    def add_song_to_playlist(self, parent):
        """
        Добавляет выбранную песню в выбранный плейлист.

        :param parent: Родительский виджет.
        """
        try:
            if not self.check_list_not_empty(parent.loaded_songs_listWidget, "No songs in the list!"):
                return
            current_selection = parent.loaded_songs_listWidget.currentRow()
            if current_selection < 0 or current_selection >= parent.loaded_songs_listWidget.count():
                QMessageBox.information(parent, "Attention", "No song selected!")
                return

            item = parent.loaded_songs_listWidget.item(current_selection)
            if not item:
                QMessageBox.information(parent, "Attention", "No song selected!")
                return
            current_song = item.data(Qt.UserRole)

            playlist, ok = self.ui_manager.select_playlist(parent)
            if not ok:  # Пользователь нажал "Отмена"
                return
            if playlist == "--Click to Select--":
                QMessageBox.information(parent, "Add song to playlist", "No playlist was selected")
                return

            self.db_manager.add_song_to_playlist(playlist, current_song)
        except IntegrityError:
            QMessageBox.warning(parent, "Warning", f"Song already in {playlist}.")
        except Exception as e:
            QMessageBox.critical(parent, "Error", f"Error adding to {playlist}: {e}")

    def add_all_to_playlist(self, parent):
        """
        Добавляет все песни из списка в выбранный плейлист.

        :param parent: Родительский виджет.
        """
        try:
            if not self.check_list_not_empty(parent.loaded_songs_listWidget, "List of songs is empty!"):
                return

            playlist, ok = self.ui_manager.select_playlist(parent)
            if not ok:
                return
            if playlist == "--Click to Select--":
                QMessageBox.information(
                    parent, "Add song to playlist", "No playlist was selected"
                )
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
                    # Если песня уже была в избранном, просто пропускаем
                    pass
            QMessageBox.information(
                parent, "Success", f"{added_count} songs added to {playlist}."
            )
        except Exception as e:
            QMessageBox.critical(
                parent, "Error", f"Error adding all songs to {playlist}: {e}"
            )

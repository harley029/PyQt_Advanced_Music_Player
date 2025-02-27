from PyQt5.QtWidgets import QListWidget, QMainWindow
from PyQt5.QtCore import Qt

from interfaces.interfaces import IListWidgetProvider
from utils.message_manager import messanger


class ListValidator:
    @staticmethod
    def check_list_not_empty(
        list_widget: QListWidget, message: str = "No songs in the list!"
    ) -> bool:
        if not list_widget or list_widget.count() == 0:
            messanger.show_warning(None, "Warning", message)
            return False
        return True

    @staticmethod
    def check_item_selected(
        list_widget: QListWidget,
        parent,
        title: str = "Attention",
        message: str = "No song selected!",
    ) -> bool:
        selected_items = list_widget.selectedItems()
        if not selected_items:
            messanger.show_info(parent, title, message)
            return False
        return True


class ListWidgetProvider(IListWidgetProvider):
    """Предоставляет доступ к списковым виджетам."""

    def __init__(self, ui: QMainWindow):
        self.ui = ui
        self.widget_map = {
            0: self.ui.loaded_songs_listWidget,
            1: self.ui.playlists_listWidget,
            2: self.ui.favourites_listWidget,
        }

    def get_current_widget(self):
        idx = self.ui.stackedWidget.currentIndex()
        return self.widget_map.get(idx)

    def register_widget(self, index, widget):
        """Позволяет добавлять новые виджеты без изменения кода."""
        self.widget_map[index] = widget

    def get_currently_selected_song(self):
        """Получить выбранную песню из текущего виджета"""
        widget = self.get_current_widget()
        if not widget or widget.count() == 0 or not widget.currentItem():
            return None

        return widget.currentItem().data(Qt.UserRole)


list_validator = ListValidator()

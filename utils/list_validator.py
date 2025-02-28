from PyQt5.QtWidgets import QListWidget
from PyQt5.QtCore import Qt

from interfaces.interfaces import IListWidgetProvider, IUIProvider
from utils.message_manager import messanger


class ListValidator:
    """
    Validates list widgets and their selections.
    Provides static methods to check list state and item selection.
    """
    @staticmethod
    def check_list_not_empty(
        list_widget: QListWidget, message: str = "No songs in the list!"
    ) -> bool:
        """
        Checks if the list widget is not empty.

        Args:
            list_widget (QListWidget): The list widget to check
            message (str, optional): Warning message to display if empty. Defaults to "No songs in the list!"

        Returns:
            bool: True if the list is not empty, False otherwise
        """
        if list_widget is None:
            messanger.show_warning(None, "Warning", "List widget is not provided!")
            return False
        if list_widget.count() == 0:
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
        """
        Checks if any item is selected in the list widget.

        Args:
            list_widget (QListWidget): The list widget to check
            parent: Parent widget for displaying messages
            title (str, optional): Title for the info message. Defaults to "Attention"
            message (str, optional): Message to display if no item selected. Defaults to "No song selected!"

        Returns:
            bool: True if an item is selected, False otherwise
        """
        selected_items = list_widget.selectedItems()
        if not selected_items:
            messanger.show_info(parent, title, message)
            return False
        return True


class ListWidgetProvider(IListWidgetProvider):
    """
    Provides access to list widgets.
    Implements the IListWidgetProvider interface for managing list widgets.
    """

    def __init__(self, ui_provider: IUIProvider):
        """
        Initializes the ListWidgetProvider with a UI instance.

        Args:
            ui (Ui_MusicApp): The UI instance containing the list widgets
        """
        self.ui_provider = ui_provider
        self.widget_map = {
            0: self.ui_provider.get_loaded_songs_widget(),
            1: self.ui_provider.get_playlists_widget(),
            2: self.ui_provider.get_favourites_widget(),
        }

    def get_current_widget(self):
        """
        Gets the currently active list widget based on stacked widget index.

        Returns:
            QListWidget: The currently active list widget or None if not found
        """
        idx = self.ui_provider.get_stacked_widget().currentIndex()
        return self.widget_map.get(idx)

    def register_widget(self, index, widget):
        """
        Allows adding new widgets without modifying code.

        Args:
            index (int): The index to assign to the widget
            widget (QListWidget): The widget to register
        """
        self.widget_map[index] = widget

    def get_currently_selected_song(self):
        """
        Gets the currently selected song from the active widget.

        Returns:
            Any: The song data stored in UserRole or None if no selection
        """
        widget = self.get_current_widget()
        if not widget or widget.count() == 0 or not widget.currentItem():
            return None
        return widget.currentItem().data(Qt.UserRole)


list_validator = ListValidator()

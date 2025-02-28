from typing import Optional
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtCore import Qt
from interfaces.interfaces import IUIProvider


class ListManager:
    """
    Manager class for handling list widget operations.

    This class provides functionality to work with the currently active list widget
    in the UI, including retrieving selected items and clearing the widget.
    """

    def __init__(self, ui_provider: IUIProvider):
        """
        Initialize the ListManager with a UI provider.

        :param ui_provider: An object implementing the IUIProvider interface
                           which provides access to UI components.
        """
        self.ui_provider = ui_provider

    def get_current_widget(self) -> QListWidget:
        """
        Get the currently displayed list widget.

        :return: The currently active QListWidget from the stacked widget.
        """
        return self.ui_provider.get_stacked_widget().currentWidget()

    def get_selected_song(self) -> Optional[str]:
        """
        Get the currently displayed list widget.

        :return: The currently active QListWidget from the stacked widget.
        """
        widget = self.get_current_widget()
        if widget is None or widget.count() == 0 or not widget.currentItem():
            return None
        return widget.currentItem().data(Qt.UserRole)

    def clear_current_widget(self):
        """
        Clear all items from the currently active list widget.

        If no widget is active, this method does nothing.
        """
        widget = self.get_current_widget()
        if widget:
            widget.clear()

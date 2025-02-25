from PyQt5.QtWidgets import QListWidget
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


list_validator = ListValidator()

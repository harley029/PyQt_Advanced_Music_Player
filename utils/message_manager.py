from PyQt5.QtWidgets import QMessageBox


class MessageManager:
    """Centralized message management for the application."""

    @staticmethod
    def show_info(parent, title, message):
        """
        Display an informational message.

        Args:
            parent: The parent widget for the message box
            title (str): The title of the message box
            message (str): The content to display in the message box
        """
        QMessageBox.information(parent, title, message)

    @staticmethod
    def show_warning(parent, title, message):
        """
        Display a warning message.

        Args:
            parent: The parent widget for the message box
            title (str): The title of the message box
            message (str): The warning content to display in the message box
        """
        QMessageBox.warning(parent, title, message)

    @staticmethod
    def show_critical(parent, title, message, exception=None):
        """
        Display a critical error message.

        Args:
            parent: The parent widget for the message box
            title (str): The title of the message box
            message (str): The error message to display
            exception (Exception, optional): An exception object whose details
                                           will be appended to the message
        """
        if exception is not None:
            message += f"\nError details: {str(exception)}"
        QMessageBox.critical(parent, title, message)

    @staticmethod
    def show_question(parent, title, message):
        """
        Display a question message with 'Yes' and 'No' options.

        Args:
            parent: The parent widget for the message box
            title (str): The title of the message box
            message (str): The question to display

        Returns:
            QMessageBox.StandardButton: The button clicked by the user
                                       (QMessageBox.Yes or QMessageBox.No)
        """
        return QMessageBox.question(
            parent, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )


messanger = MessageManager()

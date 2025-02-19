from PyQt5.QtWidgets import QAction


class CommandAction(QAction):
    """
    A QAction wrapper that implements the Command pattern.

    This class extends QAction to provide command pattern functionality.
    When triggered, it executes the command's execute() method that was
    passed during initialization.

    Attributes:
        command: An object implementing the ICommand interface that will be
                executed when the action is triggered.
    """

    def __init__(self, icon, text, parent, command):
        """
        Initialize a new CommandAction instance.

        Args:
            icon: Icon to be displayed for the QAction
            text: Text label for the QAction
            parent: Parent widget (typically the main window)
            command: Object implementing ICommand interface that will be
                    executed when this action is triggered

        Note:
            The command object must implement the execute() method as per
            the ICommand interface.
        """
        super().__init__(icon, text, parent)
        self.command = command
        self.triggered.connect(self.on_triggered)

    def on_triggered(self):
        """
        Handle the action's triggered signal.

        Called automatically when the action is triggered (e.g., when the user
        clicks a menu item or toolbar button). Delegates the execution to the
        stored command object by calling its execute() method.
        """
        self.command.execute()

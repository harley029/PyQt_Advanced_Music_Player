from PyQt5.QtWidgets import QAction


class CommandAction(QAction):
    """
    QAction, обёрнутый в объект-команду. При срабатывании (triggered)
    вызывается метод execute() переданной команды.
    """

    def __init__(self, icon, text, parent, command):
        """
        Инициализирует CommandAction.

        :param icon: Иконка для QAction.
        :param text: Текст для QAction.
        :param parent: Родительский объект (обычно главное окно).
        :param command: Объект, реализующий интерфейс ICommand.
        """
        super().__init__(icon, text, parent)
        self.command = command
        self.triggered.connect(self.on_triggered)

    def on_triggered(self):
        """
        Вызывается при срабатывании действия и делегирует выполнение команде.
        """
        self.command.execute()

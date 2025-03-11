import sys
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject
import pytest

from interfaces.context.command_action import CommandAction


@pytest.fixture(scope="session")
def app():
    """Фикстура для создания QApplication, если его ещё нет."""

    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    return application


def test_command_action_initialization():
    """
    Проверяем, что при создании CommandAction переданный объект команды
    сохраняется в атрибуте command.
    """
    # Создаем мок-команду с методом execute
    mock_command = MagicMock()
    icon = QIcon()
    text = "Test Action"
    parent = QObject()

    action = CommandAction(icon, text, parent, mock_command)

    # Проверяем, что command сохранён правильно
    assert action.command == mock_command


def test_command_action_trigger():
    """
    Проверяем, что при срабатывании сигнала triggered (или вызове on_triggered())
    вызывается метод execute() у переданной команды.
    """
    mock_command = MagicMock()
    icon = QIcon()
    text = "Test Action"
    parent = QObject()

    action = CommandAction(icon, text, parent, mock_command)

    # Вместо эмуляции сигнала можно вызвать напрямую on_triggered()
    action.on_triggered()

    # Проверяем, что execute() вызван ровно один раз
    mock_command.execute.assert_called_once()

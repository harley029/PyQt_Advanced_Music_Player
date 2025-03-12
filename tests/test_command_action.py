import sys
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject
import pytest

from interfaces.context.command_action import CommandAction


@pytest.fixture(scope="session")
def app():
    """
    Fixture to create a QApplication instance for the test session.

    This fixture ensures that a QApplication instance exists, which is required for
    QtWidgets components testing. If an instance already exists, it returns that
    instance instead of creating a new one.

    Returns:
        QApplication: The application instance to be used by all tests.
    """
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    return application


def test_command_action_initialization():
    """
    Test that CommandAction correctly stores the command object during initialization.

    This test verifies that when a CommandAction is instantiated with a command object,
    the command is properly stored in the CommandAction's command attribute.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the command attribute of the CommandAction does not match
                       the mock command object passed during initialization.
    """
    mock_command = MagicMock()
    icon = QIcon()
    text = "Test Action"
    parent = QObject()

    action = CommandAction(icon, text, parent, mock_command)
    assert action.command == mock_command


def test_command_action_trigger():
    """
    Test that CommandAction executes its command when triggered.

    This test verifies that when the on_triggered() method of a CommandAction instance
    is called (which would be connected to the triggered signal in practice), it
    correctly delegates to the execute() method of the command object that was
    passed during initialization.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the execute() method of the command object is not called
                       exactly once when the action is triggered.
    """
    mock_command = MagicMock()
    icon = QIcon()
    text = "Test Action"
    parent = QObject()

    action = CommandAction(icon, text, parent, mock_command)
    action.on_triggered()
    mock_command.execute.assert_called_once()

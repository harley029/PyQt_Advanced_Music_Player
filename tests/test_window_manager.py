from unittest.mock import MagicMock
from PyQt5.QtCore import Qt, QPoint
import pytest

from controllers.window_manager import WindowManager


class TestWindowManager:
    """
    Test suite for the WindowManager class.

    This class contains tests that verify the behavior of the WindowManager class,
    which handles window positioning, dragging, and appearance settings.
    """

    @pytest.fixture
    def mock_window(self):
        """
        Create a mock window object for testing.

        This fixture creates a mock window with a predefined position
        that can be used in window manager tests.

        Returns:
            MagicMock: A mock window object positioned at (100, 100).
        """
        window = MagicMock()
        window.pos.return_value = QPoint(100, 100)
        return window

    @pytest.fixture
    def window_manager(self, mock_window):
        """
        Create a WindowManager instance for testing.

        This fixture creates a WindowManager instance using the mock_window fixture,
        allowing tests to verify the window manager's behavior without requiring
        an actual window.

        Args:
            mock_window: The mock window fixture.

        Returns:
            WindowManager: A window manager instance initialized with the mock window.
        """
        return WindowManager(mock_window)

    def test_init(self, mock_window, window_manager):
        """
        Test the initialization of WindowManager.

        Verifies that the WindowManager correctly:
        1. Stores the provided window reference
        2. Captures the initial window position

        Args:
            mock_window: The mock window fixture.
            window_manager: The window manager fixture.
        """
        assert window_manager.window == mock_window
        assert window_manager.initialPosition == QPoint(100, 100)
        mock_window.pos.assert_called_once()

    def test_setup_window(self, window_manager):
        """
        Test the setup_window method.

        Verifies that the setup_window method correctly:
        1. Sets the window to have a translucent background
        2. Removes the window frame (FramelessWindowHint)

        Args:
            window_manager: The window manager fixture.
        """
        window_manager.setup_window()
        window_manager.window.setAttribute.assert_called_once_with(
            Qt.WA_TranslucentBackground
        )
        window_manager.window.setWindowFlags.assert_called_once_with(
            Qt.FramelessWindowHint
        )

    def test_handleMousePressEvent_left_button(self, window_manager):
        """
        Test handling mouse press events with the left button.

        Verifies that when a left mouse button press event occurs:
        1. The initial position is updated to the global cursor position

        Args:
            window_manager: The window manager fixture.
        """
        mock_event = MagicMock()
        mock_event.button.return_value = Qt.LeftButton
        mock_event.globalPos.return_value = QPoint(200, 300)
        window_manager.handleMousePressEvent(mock_event)
        assert window_manager.initialPosition == QPoint(200, 300)
        mock_event.button.assert_called_once()
        mock_event.globalPos.assert_called_once()

    def test_handleMousePressEvent_other_button(self, window_manager):
        """
        Test handling mouse press events with buttons other than the left button.

        Verifies that when a non-left mouse button press event occurs:
        1. The initial position remains unchanged
        2. The global cursor position is not queried

        Args:
            window_manager: The window manager fixture.
        """
        mock_event = MagicMock()
        mock_event.button.return_value = Qt.RightButton
        initial_pos = window_manager.initialPosition
        window_manager.handleMousePressEvent(mock_event)
        assert window_manager.initialPosition == initial_pos
        mock_event.button.assert_called_once()
        mock_event.globalPos.assert_not_called()

    def test_handleMouseMoveEvent_left_button(self, window_manager):
        """
        Test handling mouse move events with the left button pressed.

        Verifies that when the left button is pressed during a mouse move event:
        1. The window is moved to the correct position
        2. The initial position is updated
        3. The event is accepted

        Args:
            window_manager: The window manager fixture.
        """
        mock_event = MagicMock()
        mock_event.buttons.return_value = Qt.LeftButton
        mock_event.globalPos.return_value = QPoint(250, 350)
        window_manager.initialPosition = QPoint(200, 300)
        window_manager.window.pos.return_value = QPoint(100, 100)
        window_manager.handleMouseMoveEvent(mock_event)
        window_manager.window.move.assert_called_once_with(QPoint(150, 150))
        assert window_manager.initialPosition == QPoint(250, 350)
        mock_event.accept.assert_called_once()
        assert mock_event.buttons.call_count == 1
        assert mock_event.globalPos.call_count == 2

    def test_handleMouseMoveEvent_no_left_button(self, window_manager):
        """
        Test handling mouse move events without the left button pressed.

        Verifies that when the left button is not pressed during a mouse move event:
        1. The window position remains unchanged
        2. The initial position remains unchanged
        3. The event is not accepted

        Args:
            window_manager: The window manager fixture.
        """
        mock_event = MagicMock()
        mock_event.buttons.return_value = Qt.NoButton
        initial_pos = window_manager.initialPosition
        window_manager.handleMouseMoveEvent(mock_event)
        window_manager.window.move.assert_not_called()
        assert window_manager.initialPosition == initial_pos
        mock_event.accept.assert_not_called()
        mock_event.buttons.assert_called_once()
        mock_event.globalPos.assert_not_called()

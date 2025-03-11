from unittest.mock import MagicMock
from PyQt5.QtCore import Qt, QPoint
import pytest

from controllers.window_manager import WindowManager


class TestWindowManager:
    @pytest.fixture
    def mock_window(self):
        """Fixture to create a mock window object."""
        window = MagicMock()
        window.pos.return_value = QPoint(100, 100)  # Начальная позиция окна
        return window

    @pytest.fixture
    def window_manager(self, mock_window):
        """Fixture to create a WindowManager instance with a mock window."""
        return WindowManager(mock_window)

    def test_init(self, mock_window, window_manager):
        """Test initialization of WindowManager."""
        assert window_manager.window == mock_window
        assert window_manager.initialPosition == QPoint(100, 100)
        mock_window.pos.assert_called_once()

    def test_setup_window(self, window_manager):
        """Test setup_window configures window properties."""
        window_manager.setup_window()
        window_manager.window.setAttribute.assert_called_once_with(
            Qt.WA_TranslucentBackground
        )
        window_manager.window.setWindowFlags.assert_called_once_with(
            Qt.FramelessWindowHint
        )

    def test_handleMousePressEvent_left_button(self, window_manager):
        """Test handleMousePressEvent with left mouse button."""
        mock_event = MagicMock()
        mock_event.button.return_value = Qt.LeftButton
        mock_event.globalPos.return_value = QPoint(200, 300)

        window_manager.handleMousePressEvent(mock_event)

        assert window_manager.initialPosition == QPoint(200, 300)
        mock_event.button.assert_called_once()
        mock_event.globalPos.assert_called_once()

    def test_handleMousePressEvent_other_button(self, window_manager):
        """Test handleMousePressEvent with non-left mouse button."""
        mock_event = MagicMock()
        mock_event.button.return_value = Qt.RightButton
        initial_pos = window_manager.initialPosition  # Сохраняем начальную позицию

        window_manager.handleMousePressEvent(mock_event)

        assert window_manager.initialPosition == initial_pos  # Позиция не изменилась
        mock_event.button.assert_called_once()
        mock_event.globalPos.assert_not_called()

    def test_handleMouseMoveEvent_left_button(self, window_manager):
        """Test handleMouseMoveEvent with left button pressed."""
        mock_event = MagicMock()
        mock_event.buttons.return_value = Qt.LeftButton
        mock_event.globalPos.return_value = QPoint(250, 350)  # Конечная позиция мыши
        window_manager.initialPosition = QPoint(200, 300)  # Начальная позиция мыши
        window_manager.window.pos.return_value = QPoint(100, 100)  # Начальная позиция окна

        window_manager.handleMouseMoveEvent(mock_event)

        # Ожидаемая новая позиция: (100, 100) + (250, 350) - (200, 300) = (150, 150)
        window_manager.window.move.assert_called_once_with(QPoint(150, 150))
        assert window_manager.initialPosition == QPoint(250, 350)
        mock_event.accept.assert_called_once()
        assert mock_event.buttons.call_count == 1
        assert mock_event.globalPos.call_count == 2

    def test_handleMouseMoveEvent_no_left_button(self, window_manager):
        """Test handleMouseMoveEvent without left button pressed."""
        mock_event = MagicMock()
        mock_event.buttons.return_value = Qt.NoButton
        initial_pos = window_manager.initialPosition  # Сохраняем начальную позицию

        window_manager.handleMouseMoveEvent(mock_event)

        window_manager.window.move.assert_not_called()
        assert window_manager.initialPosition == initial_pos  # Позиция не изменилась
        mock_event.accept.assert_not_called()
        mock_event.buttons.assert_called_once()
        mock_event.globalPos.assert_not_called()


# if __name__ == "__main__":
#     pytest.main(["-v"])

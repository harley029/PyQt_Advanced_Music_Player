from unittest.mock import Mock, MagicMock
import pytest
from PyQt5.QtWidgets import QListWidget, QWidget, QStackedWidget
from PyQt5.QtCore import Qt

# Import the class to test
from utils.list_manager import ListManager


class TestListManager:
    @pytest.fixture
    def mock_ui_provider(self):
        """Fixture to create a mock UI provider for testing."""
        mock_provider = Mock()
        mock_stacked_widget = MagicMock(spec=QStackedWidget)
        mock_provider.get_stacked_widget.return_value = mock_stacked_widget
        return mock_provider, mock_stacked_widget

    @pytest.fixture
    def list_manager(self, mock_ui_provider):
        """Fixture to create a ListManager instance for testing."""
        manager = ListManager(mock_ui_provider[0])
        return manager

    def test_init(self, list_manager, mock_ui_provider):
        """Test that the ListManager initializes correctly."""
        assert list_manager.ui_provider == mock_ui_provider[0]

    def test_get_current_widget_when_is_list_widget(
        self, list_manager, mock_ui_provider
    ):
        """Test getting current widget when it's directly a QListWidget."""
        mock_provider, mock_stacked = mock_ui_provider
        mock_list_widget = MagicMock(spec=QListWidget)

        # Configure the mock stacked widget to return a QListWidget
        mock_stacked.currentWidget.return_value = mock_list_widget

        # Call the method under test
        result = list_manager.get_current_widget()

        # Verify the result
        assert result == mock_list_widget
        mock_stacked.currentWidget.assert_called_once()

    def test_get_current_widget_when_has_child_list_widget(
        self, list_manager, mock_ui_provider
    ):
        """Test getting current widget when it contains a child QListWidget."""
        mock_provider, mock_stacked = mock_ui_provider
        mock_container = MagicMock(spec=QWidget)
        mock_list_widget = MagicMock(spec=QListWidget)

        # Configure the mocks
        mock_stacked.currentWidget.return_value = mock_container
        mock_container.findChild.return_value = mock_list_widget

        # Call the method under test
        result = list_manager.get_current_widget()

        # Verify the result
        assert result == mock_list_widget
        mock_stacked.currentWidget.assert_called_once()
        mock_container.findChild.assert_called_once_with(QListWidget)

    def test_get_selected_song_with_selection(self, list_manager, mock_ui_provider):
        """Test getting selected song when a song is selected."""
        # Setup mock list widget with a selected item
        mock_list_widget = MagicMock(spec=QListWidget)
        mock_item = MagicMock()
        mock_item.data.return_value = "song_filename.mp3"

        mock_list_widget.count.return_value = 5
        mock_list_widget.currentItem.return_value = mock_item

        # Configure the manager to use our mock widget
        list_manager.get_current_widget = MagicMock(return_value=mock_list_widget)

        # Call the method under test
        result = list_manager.get_selected_song()

        # Verify the result
        assert result == "song_filename.mp3"
        mock_item.data.assert_called_once_with(Qt.UserRole)

    def test_get_selected_song_no_widget(self, list_manager):
        """Test getting selected song when no widget is available."""
        # Configure the manager to return None as current widget
        list_manager.get_current_widget = MagicMock(return_value=None)

        # Call the method under test
        result = list_manager.get_selected_song()

        # Verify the result
        assert result is None

    def test_get_selected_song_empty_widget(self, list_manager):
        """Test getting selected song when widget is empty."""
        # Setup mock list widget that's empty
        mock_list_widget = MagicMock(spec=QListWidget)
        mock_list_widget.count.return_value = 0

        # Configure the manager to use our mock widget
        list_manager.get_current_widget = MagicMock(return_value=mock_list_widget)

        # Call the method under test
        result = list_manager.get_selected_song()

        # Verify the result
        assert result is None

    def test_get_selected_song_no_selection(self, list_manager):
        """Test getting selected song when no item is selected."""
        # Setup mock list widget with items but no selection
        mock_list_widget = MagicMock(spec=QListWidget)
        mock_list_widget.count.return_value = 5
        mock_list_widget.currentItem.return_value = None

        # Configure the manager to use our mock widget
        list_manager.get_current_widget = MagicMock(return_value=mock_list_widget)

        # Call the method under test
        result = list_manager.get_selected_song()

        # Verify the result
        assert result is None

    def test_clear_current_widget_no_widget(self, list_manager):
        """Test clearing when no widget is available."""
        # Configure the manager to return None as current widget
        list_manager.get_current_widget = MagicMock(return_value=None)

        # Call the method under test - should not raise any exceptions
        list_manager.clear_current_widget()

    def test_get_current_widget_no_list_widget_found(self, list_manager, mock_ui_provider):
        """Test getting current widget when no QListWidget is found in the container."""
        mock_provider, mock_stacked = mock_ui_provider
        mock_container = MagicMock(spec=QWidget)

        # Configure the mocks
        mock_stacked.currentWidget.return_value = mock_container
        mock_container.findChild.return_value = None  # No QListWidget found

        # Call the method under test
        result = list_manager.get_current_widget()

        # Verify the result
        assert result is None
        mock_stacked.currentWidget.assert_called_once()
        mock_container.findChild.assert_called_once_with(QListWidget)

    def test_clear_current_widget_with_widget(self, list_manager, mock_ui_provider):
        """Test clearing the current widget when a QListWidget is available."""
        mock_provider, mock_stacked = mock_ui_provider
        mock_list_widget = MagicMock(spec=QListWidget)
        mock_item = MagicMock()
        mock_item.data.return_value = "song_filename.mp3"
        mock_list_widget.count.return_value = 5
        mock_list_widget.currentItem.return_value = mock_item

        # Use mock_ui_provider instead of overriding get_current_widget
        mock_stacked.currentWidget.return_value = mock_list_widget

        result = list_manager.get_selected_song()
        assert result == "song_filename.mp3"
        mock_item.data.assert_called_once_with(Qt.UserRole)

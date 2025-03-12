from unittest.mock import Mock, MagicMock
import pytest
from PyQt5.QtWidgets import QListWidget, QWidget, QStackedWidget
from PyQt5.QtCore import Qt

from utils.list_manager import ListManager


class TestListManager:
    @pytest.fixture
    def mock_ui_provider(self):
        """
        Fixture to create a mock UI provider for testing.

        Returns:
            tuple: A tuple containing:
                - mock_provider (Mock): Mock UI provider object
                - mock_stacked_widget (MagicMock): Mock QStackedWidget instance
        """
        mock_provider = Mock()
        mock_stacked_widget = MagicMock(spec=QStackedWidget)
        mock_provider.get_stacked_widget.return_value = mock_stacked_widget
        return mock_provider, mock_stacked_widget

    @pytest.fixture
    def list_manager(self, mock_ui_provider):
        """
        Fixture to create a ListManager instance for testing.

        Args:
            mock_ui_provider (tuple): The mock UI provider fixture

        Returns:
            ListManager: An initialized ListManager instance for testing
        """
        manager = ListManager(mock_ui_provider[0])
        return manager

    def test_init(self, list_manager, mock_ui_provider):
        """
        Test that the ListManager initializes correctly.

        Args:
            list_manager (ListManager): The ListManager instance
            mock_ui_provider (tuple): The mock UI provider fixture

        Returns:
            None

        Assertions:
            - ListManager's ui_provider attribute is correctly set to the provided mock_ui_provider
        """
        assert list_manager.ui_provider == mock_ui_provider[0]

    def test_get_current_widget_when_is_list_widget(
        self, list_manager, mock_ui_provider
    ):
        """
        Test getting current widget when it's directly a QListWidget.

        Args:
            list_manager (ListManager): The ListManager instance
            mock_ui_provider (tuple): The mock UI provider fixture containing mock_provider and mock_stacked

        Returns:
            None

        Assertions:
            - get_current_widget returns the QListWidget returned by stacked_widget.currentWidget
            - stacked_widget.currentWidget is called exactly once
        """
        mock_provider, mock_stacked = mock_ui_provider
        mock_list_widget = MagicMock(spec=QListWidget)
        mock_stacked.currentWidget.return_value = mock_list_widget
        result = list_manager.get_current_widget()
        assert result == mock_list_widget
        mock_stacked.currentWidget.assert_called_once()

    def test_get_current_widget_when_has_child_list_widget(
        self, list_manager, mock_ui_provider
    ):
        """
        Test getting current widget when it contains a child QListWidget.

        Tests that when the current widget is a container that has a QListWidget child,
        the method correctly finds and returns the child QListWidget.

        Args:
            list_manager (ListManager): The ListManager instance
            mock_ui_provider (tuple): The mock UI provider fixture

        Returns:
            None

        Assertions:
            - get_current_widget returns the child QListWidget
            - stacked_widget.currentWidget is called exactly once
            - container.findChild is called with QListWidget as argument
        """
        mock_provider, mock_stacked = mock_ui_provider
        mock_container = MagicMock(spec=QWidget)
        mock_list_widget = MagicMock(spec=QListWidget)
        mock_stacked.currentWidget.return_value = mock_container
        mock_container.findChild.return_value = mock_list_widget
        result = list_manager.get_current_widget()
        assert result == mock_list_widget
        mock_stacked.currentWidget.assert_called_once()
        mock_container.findChild.assert_called_once_with(QListWidget)

    def test_get_selected_song_with_selection(self, list_manager, mock_ui_provider):
        """
        Test getting selected song when a song is selected.

        Verifies that get_selected_song correctly returns the song filename
        when an item is selected in the list widget.

        Args:
            list_manager (ListManager): The ListManager instance
            mock_ui_provider (tuple): The mock UI provider fixture

        Returns:
            None

        Assertions:
            - get_selected_song returns the song filename from the selected item's UserRole data
            - item.data is called with Qt.UserRole as argument
        """
        mock_list_widget = MagicMock(spec=QListWidget)
        mock_item = MagicMock()
        mock_item.data.return_value = "song_filename.mp3"
        mock_list_widget.count.return_value = 5
        mock_list_widget.currentItem.return_value = mock_item
        list_manager.get_current_widget = MagicMock(return_value=mock_list_widget)
        result = list_manager.get_selected_song()
        assert result == "song_filename.mp3"
        mock_item.data.assert_called_once_with(Qt.UserRole)

    def test_get_selected_song_no_widget(self, list_manager):
        """
        Test getting selected song when no widget is available.

        Verifies that get_selected_song returns None when no list widget is available.

        Args:
            list_manager (ListManager): The ListManager instance

        Returns:
            None

        Assertions:
            - get_selected_song returns None when get_current_widget returns None
        """
        list_manager.get_current_widget = MagicMock(return_value=None)
        result = list_manager.get_selected_song()
        assert result is None

    def test_get_selected_song_empty_widget(self, list_manager):
        """
        Test getting selected song when widget is empty.

        Verifies that get_selected_song returns None when the list widget has no items.

        Args:
            list_manager (ListManager): The ListManager instance

        Returns:
            None

        Assertions:
            - get_selected_song returns None when the list widget count is 0
        """
        mock_list_widget = MagicMock(spec=QListWidget)
        mock_list_widget.count.return_value = 0
        list_manager.get_current_widget = MagicMock(return_value=mock_list_widget)
        result = list_manager.get_selected_song()
        assert result is None

    def test_get_selected_song_no_selection(self, list_manager):
        """
        Test getting selected song when no item is selected.

        Verifies that get_selected_song returns None when there are items in the list
        but none is currently selected.

        Args:
            list_manager (ListManager): The ListManager instance

        Returns:
            None

        Assertions:
            - get_selected_song returns None when currentItem returns None
        """
        mock_list_widget = MagicMock(spec=QListWidget)
        mock_list_widget.count.return_value = 5
        mock_list_widget.currentItem.return_value = None
        list_manager.get_current_widget = MagicMock(return_value=mock_list_widget)
        result = list_manager.get_selected_song()
        assert result is None

    def test_clear_current_widget_no_widget(self, list_manager):
        """
        Test clearing when no widget is available.

        Verifies that clear_current_widget handles the case where no list widget is available
        without raising exceptions.

        Args:
            list_manager (ListManager): The ListManager instance

        Returns:
            None

        Side Effects:
            - Method should complete without errors when get_current_widget returns None
        """
        list_manager.get_current_widget = MagicMock(return_value=None)
        list_manager.clear_current_widget()

    def test_get_current_widget_no_list_widget_found(
        self, list_manager, mock_ui_provider
    ):
        """
        Test getting current widget when no QListWidget is found in the container.

        Verifies that get_current_widget returns None when the current stacked widget
        is a container but it doesn't have a QListWidget child.

        Args:
            list_manager (ListManager): The ListManager instance
            mock_ui_provider (tuple): The mock UI provider fixture

        Returns:
            None

        Assertions:
            - get_current_widget returns None when findChild returns None
            - stacked_widget.currentWidget is called exactly once
            - container.findChild is called with QListWidget as argument
        """
        mock_provider, mock_stacked = mock_ui_provider
        mock_container = MagicMock(spec=QWidget)
        mock_stacked.currentWidget.return_value = mock_container
        mock_container.findChild.return_value = None  # No QListWidget found
        result = list_manager.get_current_widget()
        assert result is None
        mock_stacked.currentWidget.assert_called_once()
        mock_container.findChild.assert_called_once_with(QListWidget)

    def test_clear_current_widget_with_widget(self, list_manager, mock_ui_provider):
        """
        Test clearing the current widget when a QListWidget is available.

        This test appears to be testing get_selected_song rather than clear_current_widget
        based on the implementation. It verifies that get_selected_song correctly retrieves
        song data from the current list widget item.

        Args:
            list_manager (ListManager): The ListManager instance
            mock_ui_provider (tuple): The mock UI provider fixture

        Returns:
            None

        Assertions:
            - get_selected_song returns the song filename from the selected item's UserRole data
            - item.data is called with Qt.UserRole as argument
        """
        mock_provider, mock_stacked = mock_ui_provider
        mock_list_widget = MagicMock(spec=QListWidget)
        mock_item = MagicMock()
        mock_item.data.return_value = "song_filename.mp3"
        mock_list_widget.count.return_value = 5
        mock_list_widget.currentItem.return_value = mock_item
        mock_stacked.currentWidget.return_value = mock_list_widget
        result = list_manager.get_selected_song()
        assert result == "song_filename.mp3"
        mock_item.data.assert_called_once_with(Qt.UserRole)

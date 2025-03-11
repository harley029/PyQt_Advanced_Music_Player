from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QListWidget, QStackedWidget

import pytest

from utils.list_validator import ListValidator, ListWidgetProvider


class TestListValidator:
    @pytest.fixture
    def mock_list_widget(self):
        """Fixture to create a mock list widget for testing."""
        return MagicMock(spec=QListWidget)

    @pytest.fixture
    def mock_messanger(self):
        """Fixture to create a mock for the messanger module."""
        with patch("utils.list_validator.messanger") as mock:
            yield mock

    def test_check_list_not_empty_with_items(self, mock_list_widget, mock_messanger):
        """Test check_list_not_empty when list has items."""
        # Configure mock to have items
        mock_list_widget.count.return_value = 5

        # Call the method
        result = ListValidator.check_list_not_empty(mock_list_widget)

        # Verify the result
        assert result is True
        mock_list_widget.count.assert_called_once()
        mock_messanger.show_warning.assert_not_called()

    def test_check_list_not_empty_when_empty(self, mock_list_widget, mock_messanger):
        """Test check_list_not_empty when list is empty."""
        # Configure mock to be empty
        mock_list_widget.count.return_value = 0

        # Call the method
        result = ListValidator.check_list_not_empty(mock_list_widget)

        # Verify the result
        assert result is False
        mock_list_widget.count.assert_called_once()
        mock_messanger.show_warning.assert_called_once_with(
            None, "Warning", "No songs in the list!"
        )

    def test_check_list_not_empty_with_custom_message(
        self, mock_list_widget, mock_messanger
    ):
        """Test check_list_not_empty with custom message."""
        # Configure mock to be empty
        mock_list_widget.count.return_value = 0
        custom_message = "The playlist is empty!"

        # Call the method
        result = ListValidator.check_list_not_empty(mock_list_widget, custom_message)

        # Verify the result
        assert result is False
        mock_messanger.show_warning.assert_called_once_with(
            None, "Warning", custom_message
        )

    def test_check_list_not_empty_when_none(self, mock_messanger):
        """Test check_list_not_empty when list widget is None."""
        # Call the method with None
        result = ListValidator.check_list_not_empty(None)

        # Verify the result
        assert result is False
        mock_messanger.show_warning.assert_called_once_with(
            None, "Warning", "List widget is not provided!"
        )

    def test_check_item_selected_with_selection(self, mock_list_widget, mock_messanger):
        """Test check_item_selected when an item is selected."""
        # Configure mock to have a selected item
        mock_list_widget.selectedItems.return_value = [MagicMock()]
        parent = MagicMock()

        # Call the method
        result = ListValidator.check_item_selected(mock_list_widget, parent)

        # Verify the result
        assert result is True
        mock_list_widget.selectedItems.assert_called_once()
        mock_messanger.show_info.assert_not_called()

    def test_check_item_selected_without_selection(
        self, mock_list_widget, mock_messanger
    ):
        """Test check_item_selected when no item is selected."""
        # Configure mock to have no selected items
        mock_list_widget.selectedItems.return_value = []
        parent = MagicMock()

        # Call the method
        result = ListValidator.check_item_selected(mock_list_widget, parent)

        # Verify the result
        assert result is False
        mock_list_widget.selectedItems.assert_called_once()
        mock_messanger.show_info.assert_called_once_with(
            parent, "Attention", "No song selected!"
        )

    def test_check_item_selected_with_custom_message(
        self, mock_list_widget, mock_messanger
    ):
        """Test check_item_selected with custom title and message."""
        # Configure mock to have no selected items
        mock_list_widget.selectedItems.return_value = []
        parent = MagicMock()
        custom_title = "Select an Item"
        custom_message = "Please select a song to continue!"

        # Call the method
        result = ListValidator.check_item_selected(
            mock_list_widget, parent, custom_title, custom_message
        )

        # Verify the result
        assert result is False
        mock_messanger.show_info.assert_called_once_with(
            parent, custom_title, custom_message
        )


class TestListWidgetProvider:
    @pytest.fixture
    def mock_ui_provider(self):
        """Fixture to create a mock UI provider for testing."""
        mock_provider = MagicMock()

        # Mock the list widgets
        mock_loaded_songs = MagicMock(spec=QListWidget)
        mock_playlists = MagicMock(spec=QListWidget)
        mock_favourites = MagicMock(spec=QListWidget)

        # Set up the methods to return the mock widgets
        mock_provider.get_loaded_songs_widget.return_value = mock_loaded_songs
        mock_provider.get_playlists_widget.return_value = mock_playlists
        mock_provider.get_favourites_widget.return_value = mock_favourites

        # Mock the stacked widget
        mock_stacked = MagicMock(spec=QStackedWidget)
        mock_provider.get_stacked_widget.return_value = mock_stacked

        return (
            mock_provider,
            mock_stacked,
            {0: mock_loaded_songs, 1: mock_playlists, 2: mock_favourites},
        )

    @pytest.fixture
    def list_widget_provider(self, mock_ui_provider):
        """Fixture to create a ListWidgetProvider instance for testing."""
        provider = ListWidgetProvider(mock_ui_provider[0])
        return provider

    def test_init(self, list_widget_provider, mock_ui_provider):
        """Test initialization of ListWidgetProvider."""
        mock_provider, _, mock_widgets = mock_ui_provider

        # Verify the UI provider is set correctly
        assert list_widget_provider.ui_provider == mock_provider

        # Verify the widget map is set up correctly
        assert list_widget_provider.widget_map == mock_widgets

        # Verify that the getter methods were called
        mock_provider.get_loaded_songs_widget.assert_called_once()
        mock_provider.get_playlists_widget.assert_called_once()
        mock_provider.get_favourites_widget.assert_called_once()

    def test_get_current_widget(self, list_widget_provider, mock_ui_provider):
        """Test get_current_widget with different stacked widget indexes."""
        _, mock_stacked, mock_widgets = mock_ui_provider

        # Test for each index
        for idx in range(3):
            # Set up the current index
            mock_stacked.currentIndex.return_value = idx

            # Call the method
            result = list_widget_provider.get_current_widget()

            # Verify the result
            assert result == mock_widgets[idx]
            mock_stacked.currentIndex.assert_called()

    def test_get_current_widget_unknown_index(
        self, list_widget_provider, mock_ui_provider
    ):
        """Test get_current_widget with an index not in the widget map."""
        _, mock_stacked, _ = mock_ui_provider

        # Set up an unknown index
        mock_stacked.currentIndex.return_value = 99

        # Call the method
        result = list_widget_provider.get_current_widget()

        # Verify the result is None
        assert result is None
        mock_stacked.currentIndex.assert_called_once()

    def test_register_widget(self, list_widget_provider):
        """Test registering a new widget."""
        # Create a mock widget to register
        new_widget = MagicMock(spec=QListWidget)
        new_index = 3

        # Call the method
        list_widget_provider.register_widget(new_index, new_widget)

        # Verify the widget was added to the map
        assert list_widget_provider.widget_map[new_index] == new_widget

    def test_get_currently_selected_song_no_widget(self, list_widget_provider):
        """Test get_currently_selected_song when no widget is available."""
        # Set up no current widget
        list_widget_provider.get_current_widget = MagicMock(return_value=None)

        # Call the method
        result = list_widget_provider.get_currently_selected_song()

        # Verify the result
        assert result is None

    def test_get_currently_selected_song_empty_widget(self, list_widget_provider):
        """Test get_currently_selected_song when widget is empty."""
        # Set up empty current widget
        current_widget = MagicMock(spec=QListWidget)
        list_widget_provider.get_current_widget = MagicMock(return_value=current_widget)

        current_widget.count.return_value = 0

        # Call the method
        result = list_widget_provider.get_currently_selected_song()

        # Verify the result
        assert result is None

    def test_get_currently_selected_song_no_selection(self, list_widget_provider):
        """Test get_currently_selected_song when no item is selected."""
        # Set up current widget with no selection
        current_widget = MagicMock(spec=QListWidget)
        list_widget_provider.get_current_widget = MagicMock(return_value=current_widget)

        current_widget.count.return_value = 5
        current_widget.currentItem.return_value = None

        # Call the method
        result = list_widget_provider.get_currently_selected_song()

        # Verify the result
        assert result is None

    # def test_get_currently_selected_song_with_selection(self, list_widget_provider):
    #     current_widget = MagicMock(spec=QListWidget)
    #     list_widget_provider.get_current_widget = MagicMock(return_value=current_widget)
    #     mock_item = MagicMock()
    #     song_data = "song_filename.mp3"
    #     current_widget.currentItem.return_value = mock_item
    #     mock_item.data.return_value = song_data
    #     current_widget.count.return_value = 5

    #     print(f"Widget: {list_widget_provider.get_current_widget()}")
    #     print(f"Count: {current_widget.count()}")
    #     print(f"CurrentItem: {current_widget.currentItem()}")
    #     print(f"Data: {mock_item.data(Qt.UserRole)}")

    #     result = list_widget_provider.get_currently_selected_song()
    #     assert result == song_data, f"Expected {song_data}, got {result}"

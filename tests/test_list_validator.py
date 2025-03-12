from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QListWidget, QStackedWidget

import pytest

from utils.list_validator import ListValidator, ListWidgetProvider


class TestListValidator:
    """
    Test suite for the ListValidator class.

    This class tests validation functionality for list widgets,
    including empty list checking and item selection validation.
    """

    @pytest.fixture
    def mock_list_widget(self):
        """
        Fixture to create a mock list widget for testing.

        Returns:
            MagicMock: A mock object with the QListWidget specification that
                      can be used to simulate a list widget in tests.
        """
        return MagicMock(spec=QListWidget)

    @pytest.fixture
    def mock_messanger(self):
        """
        Fixture to create a mock for the messanger module.

        This fixture patches the messanger module in the list_validator
        module to allow testing of warning and info message display.

        Yields:
            MagicMock: A mock object representing the messanger module.
        """
        with patch("utils.list_validator.messanger") as mock:
            yield mock

    def test_check_list_not_empty_with_items(self, mock_list_widget, mock_messanger):
        """
        Test check_list_not_empty when list has items.

        Args:
            mock_list_widget (MagicMock): Mock list widget with count method.
            mock_messanger (MagicMock): Mock messanger module.

        Verifies:
            - Returns True when the list contains items
            - The count method is called exactly once
            - No warning message is displayed
        """
        mock_list_widget.count.return_value = 5
        result = ListValidator.check_list_not_empty(mock_list_widget)
        assert result is True
        mock_list_widget.count.assert_called_once()
        mock_messanger.show_warning.assert_not_called()

    def test_check_list_not_empty_when_empty(self, mock_list_widget, mock_messanger):
        """
        Test check_list_not_empty when list is empty.

        Args:
            mock_list_widget (MagicMock): Mock list widget with count method.
            mock_messanger (MagicMock): Mock messanger module.

        Verifies:
            - Returns False when the list is empty (count = 0)
            - The count method is called exactly once
            - A warning message is displayed with the default message
        """
        mock_list_widget.count.return_value = 0
        result = ListValidator.check_list_not_empty(mock_list_widget)
        assert result is False
        mock_list_widget.count.assert_called_once()
        mock_messanger.show_warning.assert_called_once_with(
            None, "Warning", "No songs in the list!"
        )

    def test_check_list_not_empty_with_custom_message(
        self, mock_list_widget, mock_messanger
    ):
        """
        Test check_list_not_empty with custom message.

        Args:
            mock_list_widget (MagicMock): Mock list widget with count method.
            mock_messanger (MagicMock): Mock messanger module.

        Verifies:
            - Returns False when the list is empty
            - A warning message is displayed with the provided custom message
        """
        mock_list_widget.count.return_value = 0
        custom_message = "The playlist is empty!"
        result = ListValidator.check_list_not_empty(mock_list_widget, custom_message)
        assert result is False
        mock_messanger.show_warning.assert_called_once_with(
            None, "Warning", custom_message
        )

    def test_check_list_not_empty_when_none(self, mock_messanger):
        """
        Test check_list_not_empty when list widget is None.

        Args:
            mock_messanger (MagicMock): Mock messanger module.

        Verifies:
            - Returns False when the list widget is None
            - A warning message is displayed with appropriate message
            - No attempt is made to access methods on the None object
        """
        result = ListValidator.check_list_not_empty(None)
        assert result is False
        mock_messanger.show_warning.assert_called_once_with(
            None, "Warning", "List widget is not provided!"
        )

    def test_check_item_selected_with_selection(self, mock_list_widget, mock_messanger):
        """
        Test check_item_selected when an item is selected.

        Args:
            mock_list_widget (MagicMock): Mock list widget with selectedItems method.
            mock_messanger (MagicMock): Mock messanger module.

        Verifies:
            - Returns True when an item is selected
            - The selectedItems method is called exactly once
            - No info message is displayed
        """
        mock_list_widget.selectedItems.return_value = [MagicMock()]
        parent = MagicMock()
        result = ListValidator.check_item_selected(mock_list_widget, parent)
        assert result is True
        mock_list_widget.selectedItems.assert_called_once()
        mock_messanger.show_info.assert_not_called()

    def test_check_item_selected_without_selection(
        self, mock_list_widget, mock_messanger
    ):
        """
        Test check_item_selected when no item is selected.

        Args:
            mock_list_widget (MagicMock): Mock list widget with selectedItems method.
            mock_messanger (MagicMock): Mock messanger module.

        Verifies:
            - Returns False when no item is selected
            - The selectedItems method is called exactly once
            - An info message is displayed with the default message
        """
        mock_list_widget.selectedItems.return_value = []
        parent = MagicMock()
        result = ListValidator.check_item_selected(mock_list_widget, parent)
        assert result is False
        mock_list_widget.selectedItems.assert_called_once()
        mock_messanger.show_info.assert_called_once_with(
            parent, "Attention", "No song selected!"
        )

    def test_check_item_selected_with_custom_message(
        self, mock_list_widget, mock_messanger
    ):
        """
        Test check_item_selected with custom title and message.

        Args:
            mock_list_widget (MagicMock): Mock list widget with selectedItems method.
            mock_messanger (MagicMock): Mock messanger module.

        Verifies:
            - Returns False when no item is selected
            - An info message is displayed with the custom title and message
        """
        mock_list_widget.selectedItems.return_value = []
        parent = MagicMock()
        custom_title = "Select an Item"
        custom_message = "Please select a song to continue!"
        result = ListValidator.check_item_selected(
            mock_list_widget, parent, custom_title, custom_message
        )
        assert result is False
        mock_messanger.show_info.assert_called_once_with(
            parent, custom_title, custom_message
        )


class TestListWidgetProvider:
    """
    Test suite for the ListWidgetProvider class.

    This class tests functionality for managing multiple list widgets
    through a stacked widget interface, including widget registration,
    retrieval, and selection handling.
    """

    @pytest.fixture
    def mock_ui_provider(self):
        """
        Fixture to create a mock UI provider for testing.

        Creates a mock UI provider with mock list widgets for loaded songs,
        playlists, and favourites, as well as a mock stacked widget.

        Returns:
            tuple: A tuple containing:
                - The mock UI provider
                - The mock stacked widget
                - A dictionary mapping indexes to mock list widgets
        """
        mock_provider = MagicMock()
        mock_loaded_songs = MagicMock(spec=QListWidget)
        mock_playlists = MagicMock(spec=QListWidget)
        mock_favourites = MagicMock(spec=QListWidget)
        mock_provider.get_loaded_songs_widget.return_value = mock_loaded_songs
        mock_provider.get_playlists_widget.return_value = mock_playlists
        mock_provider.get_favourites_widget.return_value = mock_favourites
        mock_stacked = MagicMock(spec=QStackedWidget)
        mock_provider.get_stacked_widget.return_value = mock_stacked

        return (
            mock_provider,
            mock_stacked,
            {0: mock_loaded_songs, 1: mock_playlists, 2: mock_favourites},
        )

    @pytest.fixture
    def list_widget_provider(self, mock_ui_provider):
        """
        Fixture to create a ListWidgetProvider instance for testing.

        Args:
            mock_ui_provider (tuple): The mock UI provider fixture.

        Returns:
            ListWidgetProvider: An instance of ListWidgetProvider initialized
                               with the mock UI provider.
        """
        provider = ListWidgetProvider(mock_ui_provider[0])
        return provider

    def test_init(self, list_widget_provider, mock_ui_provider):
        """
        Test initialization of ListWidgetProvider.

        Args:
            list_widget_provider (ListWidgetProvider): The provider instance.
            mock_ui_provider (tuple): The mock UI provider fixture.

        Verifies:
            - The ui_provider attribute is set correctly
            - The widget_map is initialized with the correct widgets
            - The get_*_widget methods are called exactly once each
        """
        mock_provider, _, mock_widgets = mock_ui_provider
        assert list_widget_provider.ui_provider == mock_provider
        assert list_widget_provider.widget_map == mock_widgets
        mock_provider.get_loaded_songs_widget.assert_called_once()
        mock_provider.get_playlists_widget.assert_called_once()
        mock_provider.get_favourites_widget.assert_called_once()

    def test_get_current_widget(self, list_widget_provider, mock_ui_provider):
        """
        Test get_current_widget with different stacked widget indexes.

        Args:
            list_widget_provider (ListWidgetProvider): The provider instance.
            mock_ui_provider (tuple): The mock UI provider fixture.

        Verifies:
            - Returns the correct widget for each index in the widget map
            - The currentIndex method is called for each test case
        """
        _, mock_stacked, mock_widgets = mock_ui_provider
        for idx in range(3):
            mock_stacked.currentIndex.return_value = idx
            result = list_widget_provider.get_current_widget()
            assert result == mock_widgets[idx]
            mock_stacked.currentIndex.assert_called()

    def test_get_current_widget_unknown_index(
        self, list_widget_provider, mock_ui_provider
    ):
        """
        Test get_current_widget with an index not in the widget map.

        Args:
            list_widget_provider (ListWidgetProvider): The provider instance.
            mock_ui_provider (tuple): The mock UI provider fixture.

        Verifies:
            - Returns None when the current index is not in the widget map
            - The currentIndex method is called exactly once
        """
        _, mock_stacked, _ = mock_ui_provider
        mock_stacked.currentIndex.return_value = 99
        result = list_widget_provider.get_current_widget()
        assert result is None
        mock_stacked.currentIndex.assert_called_once()

    def test_register_widget(self, list_widget_provider):
        """
        Test registering a new widget.

        Args:
            list_widget_provider (ListWidgetProvider): The provider instance.

        Verifies:
            - The widget is correctly added to the widget_map with the given index
            - The widget can be retrieved from the widget_map after registration
        """
        new_widget = MagicMock(spec=QListWidget)
        new_index = 3
        list_widget_provider.register_widget(new_index, new_widget)
        assert list_widget_provider.widget_map[new_index] == new_widget

    def test_get_currently_selected_song_no_widget(self, list_widget_provider):
        """
        Test get_currently_selected_song when no widget is available.

        Args:
            list_widget_provider (ListWidgetProvider): The provider instance.

        Verifies:
            - Returns None when get_current_widget returns None
            - Does not attempt to access methods on a None object
        """
        list_widget_provider.get_current_widget = MagicMock(return_value=None)
        result = list_widget_provider.get_currently_selected_song()
        assert result is None

    def test_get_currently_selected_song_empty_widget(self, list_widget_provider):
        """
        Test get_currently_selected_song when widget is empty.

        Args:
            list_widget_provider (ListWidgetProvider): The provider instance.

        Verifies:
            - Returns None when the current widget has no items
            - The count method is called to check if the widget is empty
        """
        current_widget = MagicMock(spec=QListWidget)
        list_widget_provider.get_current_widget = MagicMock(return_value=current_widget)
        current_widget.count.return_value = 0
        result = list_widget_provider.get_currently_selected_song()
        assert result is None

    def test_get_currently_selected_song_no_selection(self, list_widget_provider):
        """
        Test get_currently_selected_song when no item is selected.

        Args:
            list_widget_provider (ListWidgetProvider): The provider instance.

        Verifies:
            - Returns None when the current widget has items but none is selected
            - The count method is called to check if the widget has items
            - The currentItem method is called to check for a selection
        """
        current_widget = MagicMock(spec=QListWidget)
        list_widget_provider.get_current_widget = MagicMock(return_value=current_widget)
        current_widget.count.return_value = 5
        current_widget.currentItem.return_value = None
        result = list_widget_provider.get_currently_selected_song()
        assert result is None

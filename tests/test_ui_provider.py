# pylint: disable=redefined-outer-name
from unittest.mock import MagicMock
import pytest
from PyQt5.QtWidgets import QListWidget, QStackedWidget

# Import the class to test
from interfaces.interfaces import IUIProvider
from music import Ui_MusicApp
from utils.ui_provider import UIProvider


@pytest.fixture
def mock_ui():
    """Create a mock Ui_MusicApp object."""
    mock = MagicMock(spec=Ui_MusicApp)

    # Create mock widgets
    mock.loaded_songs_listWidget = MagicMock(spec=QListWidget)
    mock.playlists_listWidget = MagicMock(spec=QListWidget)
    mock.favourites_listWidget = MagicMock(spec=QListWidget)
    mock.stackedWidget = MagicMock(spec=QStackedWidget)

    return mock


@pytest.fixture
def ui_provider(mock_ui):
    """Create a UIProvider with mocked UI components."""
    return UIProvider(mock_ui)


class TestUIProvider:
    """Test suite for the UIProvider class."""

    def test_initialization(self, mock_ui):
        """Test the initialization of the UIProvider class."""
        provider = UIProvider(mock_ui)
        assert provider.main_window == mock_ui

    def test_get_loaded_songs_widget(self, ui_provider, mock_ui):
        """Test getting the loaded songs widget."""
        result = ui_provider.get_loaded_songs_widget()
        assert result == mock_ui.loaded_songs_listWidget

    def test_get_playlists_widget(self, ui_provider, mock_ui):
        """Test getting the playlists widget."""
        result = ui_provider.get_playlists_widget()
        assert result == mock_ui.playlists_listWidget

    def test_get_favourites_widget(self, ui_provider, mock_ui):
        """Test getting the favourites widget."""
        result = ui_provider.get_favourites_widget()
        assert result == mock_ui.favourites_listWidget

    def test_get_stacked_widget(self, ui_provider, mock_ui):
        """Test getting the stacked widget."""
        result = ui_provider.get_stacked_widget()
        assert result == mock_ui.stackedWidget

    def test_implements_interface(self):
        """Test that UIProvider properly implements the IUIProvider interface."""
        # Get all methods defined in the interface
        interface_methods = [
            method
            for method in dir(IUIProvider)
            if callable(getattr(IUIProvider, method)) and not method.startswith("__")
        ]

        # Check that all interface methods are implemented in UIProvider
        for method in interface_methods:
            assert hasattr(
                UIProvider, method
            ), f"Method '{method}' from IUIProvider not implemented in UIProvider"

    def test_with_real_widgets(self):
        """Test UIProvider with more realistic widget scenarios."""
        # Create a mock with more realistic behavior
        real_ui = MagicMock(spec=Ui_MusicApp)

        # Set up a list widget with items
        real_loaded_songs = MagicMock(spec=QListWidget)
        real_loaded_songs.count.return_value = 3
        real_ui.loaded_songs_listWidget = real_loaded_songs

        # Create provider with this mock
        provider = UIProvider(real_ui)
        result = provider.get_loaded_songs_widget()

        # Test the provider
        result = provider.get_loaded_songs_widget()
        assert result.count() == 3

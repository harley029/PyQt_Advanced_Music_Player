# pylint: disable=redefined-outer-name
from unittest.mock import MagicMock
import pytest
from PyQt5.QtWidgets import QListWidget, QStackedWidget

from interfaces.interfaces import IUIProvider
from music import Ui_MusicApp
from utils.ui_provider import UIProvider


@pytest.fixture
def mock_ui():
    """
    Create a mock Ui_MusicApp object for testing.

    This fixture creates a mock of the main application UI class with
    mocked list widgets for songs, playlists, and favorites, as well as
    a stacked widget for managing different views.

    Returns:
        MagicMock: A mock object that simulates the Ui_MusicApp class with
                  necessary widget attributes.
    """
    mock = MagicMock(spec=Ui_MusicApp)
    mock.loaded_songs_listWidget = MagicMock(spec=QListWidget)
    mock.playlists_listWidget = MagicMock(spec=QListWidget)
    mock.favourites_listWidget = MagicMock(spec=QListWidget)
    mock.stackedWidget = MagicMock(spec=QStackedWidget)
    return mock


@pytest.fixture
def ui_provider(mock_ui):
    """
    Create a UIProvider instance with mocked UI components.

    This fixture uses the mock_ui fixture to create a testable UIProvider
    instance that will return controlled mock widgets.

    Args:
        mock_ui: The mocked Ui_MusicApp instance from the mock_ui fixture.

    Returns:
        UIProvider: An instance of the UIProvider class initialized with mocked UI.
    """
    return UIProvider(mock_ui)


class TestUIProvider:
    """
    Test suite for the UIProvider class.

    This class contains tests to verify that the UIProvider correctly
    implements the IUIProvider interface and properly provides access
    to the UI widgets.
    """

    def test_initialization(self, mock_ui):
        """
        Test the initialization of the UIProvider class.

        Verifies that the UIProvider correctly stores a reference to
        the provided main window UI object.

        Args:
            mock_ui: The mocked Ui_MusicApp instance.

        Returns:
            None
        """
        provider = UIProvider(mock_ui)
        assert provider.main_window == mock_ui

    def test_get_loaded_songs_widget(self, ui_provider, mock_ui):
        """
        Test getting the loaded songs widget.

        Verifies that the get_loaded_songs_widget method returns
        the correct QListWidget from the main UI.

        Args:
            ui_provider: The UIProvider instance to test.
            mock_ui: The mocked Ui_MusicApp instance.

        Returns:
            None
        """
        result = ui_provider.get_loaded_songs_widget()
        assert result == mock_ui.loaded_songs_listWidget

    def test_get_playlists_widget(self, ui_provider, mock_ui):
        """
        Test getting the playlists widget.

        Verifies that the get_playlists_widget method returns
        the correct QListWidget from the main UI.

        Args:
            ui_provider: The UIProvider instance to test.
            mock_ui: The mocked Ui_MusicApp instance.

        Returns:
            None
        """
        result = ui_provider.get_playlists_widget()
        assert result == mock_ui.playlists_listWidget

    def test_get_favourites_widget(self, ui_provider, mock_ui):
        """
        Test getting the favourites widget.

        Verifies that the get_favourites_widget method returns
        the correct QListWidget from the main UI.

        Args:
            ui_provider: The UIProvider instance to test.
            mock_ui: The mocked Ui_MusicApp instance.

        Returns:
            None
        """
        result = ui_provider.get_favourites_widget()
        assert result == mock_ui.favourites_listWidget

    def test_get_stacked_widget(self, ui_provider, mock_ui):
        """
        Test getting the stacked widget.

        Verifies that the get_stacked_widget method returns
        the correct QStackedWidget from the main UI.

        Args:
            ui_provider: The UIProvider instance to test.
            mock_ui: The mocked Ui_MusicApp instance.

        Returns:
            None
        """
        result = ui_provider.get_stacked_widget()
        assert result == mock_ui.stackedWidget

    def test_implements_interface(self):
        """
        Test that UIProvider properly implements the IUIProvider interface.

        This test dynamically checks that all non-dunder methods defined in the
        IUIProvider interface are implemented by the UIProvider class.

        Returns:
            None

        Raises:
            AssertionError: If any method from the interface is not implemented.
        """
        interface_methods = [
            method
            for method in dir(IUIProvider)
            if callable(getattr(IUIProvider, method)) and not method.startswith("__")
        ]
        for method in interface_methods:
            assert hasattr(
                UIProvider, method
            ), f"Method '{method}' from IUIProvider not implemented in UIProvider"

    def test_with_real_widgets(self):
        """
        Test UIProvider with more realistic widget scenarios.

        This test creates a mock that simulates more realistic behavior
        of QListWidget by setting up return values for methods like count().
        It verifies that the UIProvider correctly interacts with widgets
        that have state and behavior.

        Returns:
            None
        """
        real_ui = MagicMock(spec=Ui_MusicApp)
        real_loaded_songs = MagicMock(spec=QListWidget)
        real_loaded_songs.count.return_value = 3
        real_ui.loaded_songs_listWidget = real_loaded_songs
        provider = UIProvider(real_ui)
        result = provider.get_loaded_songs_widget()
        # Call again to test potential caching or repeated usage
        result = provider.get_loaded_songs_widget()
        assert result.count() == 3

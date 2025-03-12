# test_utils.py
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QListWidget


def create_mock_ui_provider():
    """
    Creates a mock for the ui_provider with favourites and loaded_songs widgets.

    This function creates a mock object for the UI provider that includes
    configured mock objects for the favourites widget and loaded songs widget.
    These mocks can be used in unit tests to simulate UI interactions.

    Returns:
        tuple: Contains three items:
            - ui_provider (MagicMock): The mocked UI provider
            - favourites_widget (MagicMock): Mock for the favourites list widget
            - loaded_songs_widget (MagicMock): Mock for the loaded songs list widget
    """
    ui_provider = MagicMock()
    favourites_widget = MagicMock(spec=QListWidget)
    loaded_songs_widget = MagicMock(spec=QListWidget)
    ui_provider.get_favourites_widget.return_value = favourites_widget
    ui_provider.get_loaded_songs_widget.return_value = loaded_songs_widget
    return ui_provider, favourites_widget, loaded_songs_widget


def create_mock_music_controller(current_song="song.mp3"):
    """
    Creates a mock for the music controller with a configured media_player.

    This function creates a mock object for the music controller that includes
    a configured media player mock. The media player is set up to return the
    specified current song when queried. This allows unit tests to simulate
    the behavior of the music controller without requiring actual media playback.

    Args:
        current_song (str, optional): The filename of the song that should be
            returned as the currently playing media. Defaults to "song.mp3".

    Returns:
        MagicMock: A configured mock object for the music controller that will
                   return the specified current song when queried.
    """
    music_controller = MagicMock()
    media_player = MagicMock()
    media = MagicMock()
    media.canonicalUrl.return_value.toLocalFile.return_value = current_song
    media_player.media.return_value = media
    music_controller.media_player.return_value = media_player
    return music_controller

from interfaces.interfaces import IUIProvider
from music import Ui_MusicApp


class UIProvider(IUIProvider):
    """
    UI Provider class that implements the IUIProvider interface.

    This class provides access to various UI widgets from the main application window.
    It serves as a facade for accessing UI components throughout the application.
    """

    def __init__(self, main_window: Ui_MusicApp):
        """
        Initialize the UIProvider with the main application window.

        :param main_window: The main window UI object of the music application.
        """
        self.main_window = main_window

    def get_loaded_songs_widget(self):
        """
        Get the widget that displays loaded songs.

        :return: The list widget containing loaded songs.
        """
        return self.main_window.loaded_songs_listWidget

    def get_playlists_widget(self):
        """
        Get the widget that displays playlists.

        :return: The list widget containing playlists.
        """
        return self.main_window.playlists_listWidget

    def get_favourites_widget(self):
        """
        Get the widget that displays favourite songs.

        :return: The list widget containing favourite songs.
        """
        return self.main_window.favourites_listWidget

    def get_stacked_widget(self):
        """
        Get the stacked widget that manages multiple pages in the UI.

        :return: The stacked widget used for UI navigation.
        """
        return self.main_window.stackedWidget

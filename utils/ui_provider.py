from interfaces.interfaces import IUIProvider
# from music import Ui_MusicApp


class UIProvider(IUIProvider):

    def __init__(self, main_window):
        self.main_window = main_window

    def get_loaded_songs_widget(self):
        return self.main_window.loaded_songs_listWidget

    def get_playlists_widget(self):
        return self.main_window.playlists_listWidget

    def get_favourites_widget(self):
        return self.main_window.favourites_listWidget

    def get_stacked_widget(self):
        return self.main_window.stackedWidget

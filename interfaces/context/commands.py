from interfaces.interfaces import ICommand
from controllers.event_handler import EventHandler
from controllers.favourites_manager import FavouritesManager
from interfaces.playlists.playlist_manager import PlaylistManager


class PlayCommand(ICommand):
    """
    Конкретная команда для воспроизведения песни. При вызове execute()
    делегирует работу методу on_play_clicked() обработчика событий.
    """

    def __init__(self, event_handler: EventHandler):
        """
        :param event_handler: Объект-обработчик, у которого вызывается метод on_play_clicked().
        """
        self.event_handler = event_handler

    def execute(self):
        """
        Выполняет команду воспроизведения.
        """
        self.event_handler.on_play_clicked()


class PauseCommand(ICommand):

    def __init__(self, event_handler: EventHandler):
        self.event_handler = event_handler

    def execute(self):
        self.event_handler.on_pause_clicked()


class NextCommand(ICommand):

    def __init__(self, event_handler: EventHandler):
        self.event_handler = event_handler

    def execute(self):
        self.event_handler.on_next_previous_clicked(direction = "forward")


class PreviousCommand(ICommand):

    def __init__(self, event_handler: EventHandler):
        self.event_handler = event_handler

    def execute(self):
        self.event_handler.on_next_previous_clicked(direction="buckward")


class StopCommand(ICommand):

    def __init__(self, event_handler: EventHandler):
        self.event_handler = event_handler

    def execute(self):
        self.event_handler.on_stop_clicked()


class SelectedToFavouritesCommand(ICommand):

    def __init__(self, favourites_manager: FavouritesManager):
        self.favourites_manager = favourites_manager
        self.source_list_widget = favourites_manager.loaded_songs_listWidget

    def execute(self):
        self.favourites_manager.add_to_favourites()


class AllToFavouritesCommand(ICommand):

    def __init__(self, favourites_manager: FavouritesManager):
        self.favourites_manager = favourites_manager

    def execute(self):
        self.favourites_manager.add_all_to_favourites()


class SelectedToPlaylistCommand(ICommand):

    def __init__(self, playlist_manager: PlaylistManager, parent):
        self.playlist_manager = playlist_manager
        self.parent = parent

    def execute(self):
        self.playlist_manager.add_song_to_playlist(self.parent)


class AllToPlaylistCommand(ICommand):

    def __init__(self, playlist_manager: PlaylistManager, parent):
        self.playlist_manager = playlist_manager
        self.parent = parent

    def execute(self):
        self.playlist_manager.add_all_to_playlist(self.parent)


class DeleteSelectedFavouriteCommand(ICommand):

    def __init__(self, avourites_manager: FavouritesManager):
        self.avourites_manager = avourites_manager

    def execute(self):
        self.avourites_manager.remove_selected_favourite()


class DeleteAllFavouriteCommand(ICommand):

    def __init__(self, avourites_manager: FavouritesManager):
        self.avourites_manager = avourites_manager

    def execute(self):
        self.avourites_manager.clear_favourites()


class LoadPlaylistCommand(ICommand):

    def __init__(self, playlist_manager: PlaylistManager, parent):
        self.playlist_manager = playlist_manager
        self.parent = parent

    def execute(self):
        self.playlist_manager.load_playlist_into_widget(self.parent)


class NewPlaylistCommand(ICommand):

    def __init__(self, playlist_manager: PlaylistManager, parent):
        self.playlist_manager = playlist_manager
        self.parent = parent

    def execute(self):
        self.playlist_manager.create_playlist(self.parent)


class DeletePlaylistCommand(ICommand):

    def __init__(self, playlist_manager: PlaylistManager, parent):
        self.playlist_manager = playlist_manager
        self.parent = parent

    def execute(self):
        self.playlist_manager.remove_playlist(self.parent)


class DeleteAllPlaylistCommand(ICommand):

    def __init__(self, playlist_manager: PlaylistManager, parent):
        self.playlist_manager = playlist_manager
        self.parent = parent

    def execute(self):
        self.playlist_manager.remove_all_playlists(self.parent)

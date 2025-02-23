from interfaces.interfaces import ICommand
from interfaces.playlists.playlist_manager import PlaylistManager
from controllers.event_handler import EventHandler
from controllers.favourites_manager import FavouritesManager


class PlayCommand(ICommand):
    """
    Command for starting playback.

    Implements the ICommand interface to provide a standard way to handle play functionality.
    """

    def __init__(self, event_handler: EventHandler):
        """
        Initialize a new PlayCommand instance.

        Args:
            event_handler (EventHandler): Event handler which calls method on_play_clicked().
        """
        self.event_handler = event_handler

    def execute(self):
        """
        Execute the Play command.

        Calls the on_play_clicked method of the associated event handler.
        """
        self.event_handler.on_play_clicked()


class PauseCommand(ICommand):
    """
    Command for pausing or unpausing playback.

    Implements the ICommand interface to provide a standard way to handle pause functionality.
    """

    def __init__(self, event_handler: EventHandler):
        """
        Initialize a new PauseCommand instance.

        Args:
            event_handler (EventHandler): Event handler which calls method on_pause_clicked().
        """
        self.event_handler = event_handler

    def execute(self):
        """
        Execute the Pause command.

        Calls the on_pause_clicked method of the associated event handler.
        """
        self.event_handler.on_pause_clicked()


class NextCommand(ICommand):
    """
    Command for moving to the next track.

    Implements the ICommand interface to provide a standard way to handle next track functionality.
    """

    def __init__(self, event_handler: EventHandler):
        """
        Initialize a new NextCommand instance.

        Args:
            event_handler (EventHandler): Event handler which calls method on_next_previous_clicked().
        """
        self.event_handler = event_handler

    def execute(self):
        """
        Execute the Next command.

        Calls the on_next_previous_clicked method of the associated event handler
        with the direction set to "forward".
        """
        self.event_handler.on_next_previous_clicked(direction="forward")


class PreviousCommand(ICommand):
    """
    Command for moving to the previous track.

    Implements the ICommand interface to provide a standard way to handle previous track functionality.
    """

    def __init__(self, event_handler: EventHandler):
        """
        Initialize a new PreviousCommand instance.

        Args:
            event_handler (EventHandler): Event handler which calls method on_next_previous_clicked().
        """
        self.event_handler = event_handler

    def execute(self):
        """
        Execute the Previous command.

        Calls the on_next_previous_clicked method of the associated event handler
        with the direction set to "backward". Note: There appears to be a typo, "backward" instead of "backward".
        """
        self.event_handler.on_next_previous_clicked(direction="backward")


class StopCommand(ICommand):
    """
    Command for stopping playback.

    Implements the ICommand interface to provide a standard way to handle stop functionality.
    """

    def __init__(self, event_handler: EventHandler):
        """
        Initialize a new StopCommand instance.

        Args:
            event_handler (EventHandler): Event handler which calls method on_stop_clicked().
        """
        self.event_handler = event_handler

    def execute(self):
        """
        Execute the Stop command.

        Calls the on_stop_clicked method of the associated event handler.
        """
        self.event_handler.on_stop_clicked()


class SelectedToFavouritesCommand(ICommand):
    """
    Command for adding selected songs to favourites.

    Implements the ICommand interface to provide a standard way to handle adding songs to favourites.
    """

    def __init__(self, favourites_manager: FavouritesManager):
        """
        Initialize a new SelectedToFavouritesCommand instance.

        Args:
            favourites_manager (FavouritesManager): Manager for handling favourites-related operations.
        """
        self.favourites_manager = favourites_manager
        self.source_list_widget = favourites_manager.loaded_songs_listWidget

    def execute(self):
        """
        Execute the command to add selected songs to favourites.

        Calls the add_to_favourites method of the associated favourites manager.
        """
        self.favourites_manager.add_to_favourites()


class AllToFavouritesCommand(ICommand):
    """
    Command for adding all songs to favourites.

    Implements the ICommand interface to provide a standard way to handle adding all songs to favourites.
    """

    def __init__(self, favourites_manager: FavouritesManager):
        """
        Initialize a new AllToFavouritesCommand instance.

        Args:
            favourites_manager (FavouritesManager): Manager for handling favourites-related operations.
        """
        self.favourites_manager = favourites_manager

    def execute(self):
        """
        Execute the command to add all songs to favourites.

        Calls the add_all_to_favourites method of the associated favourites manager.
        """
        self.favourites_manager.add_all_to_favourites()


class SelectedToPlaylistCommand(ICommand):
    """
    Command for adding selected songs to a playlist.

    Implements the ICommand interface to provide a standard way to handle adding songs to a playlist.
    """

    def __init__(self, playlist_manager: PlaylistManager, parent):
        """
        Initialize a new SelectedToPlaylistCommand instance.

        Args:
            playlist_manager (PlaylistManager): Manager for handling playlist-related operations.
            parent: The parent widget or controller that contains this command.
        """
        self.playlist_manager = playlist_manager
        self.parent = parent

    def execute(self):
        """
        Execute the command to add selected songs to a playlist.

        Calls the add_song_to_playlist method of the associated playlist manager.
        """
        self.playlist_manager.add_song_to_playlist(self.parent)


class AllToPlaylistCommand(ICommand):
    """
    Command for adding all songs to a playlist.

    Implements the ICommand interface to provide a standard way to handle adding all songs to a playlist.
    """

    def __init__(self, playlist_manager: PlaylistManager, parent):
        """
        Initialize a new AllToPlaylistCommand instance.

        Args:
            playlist_manager (PlaylistManager): Manager for handling playlist-related operations.
            parent: The parent widget or controller that contains this command.
        """
        self.playlist_manager = playlist_manager
        self.parent = parent

    def execute(self):
        """
        Execute the command to add all songs to a playlist.

        Calls the add_all_to_playlist method of the associated playlist manager.
        """
        self.playlist_manager.add_all_to_playlist(self.parent)


class DeleteSelectedFavouriteCommand(ICommand):
    """
    Command for deleting selected favourite songs.

    Implements the ICommand interface to provide a standard way to handle deleting selected favourites.
    """

    def __init__(self, avourites_manager: FavouritesManager):
        """
        Initialize a new DeleteSelectedFavouriteCommand instance.

        Args:
            avourites_manager (FavouritesManager): Manager for handling favourites-related operations.
            Note: There appears to be a typo in the parameter name ('avourites_manager' vs 'favourites_manager').
        """
        self.avourites_manager = avourites_manager

    def execute(self):
        """
        Execute the command to delete selected favourite songs.

        Calls the remove_selected_favourite method of the associated favourites manager.
        """
        self.avourites_manager.remove_selected_favourite()


class DeleteAllFavouriteCommand(ICommand):
    """
    Command for deleting all favourite songs.

    Implements the ICommand interface to provide a standard way to handle deleting all favourites.
    """

    def __init__(self, avourites_manager: FavouritesManager):
        """
        Initialize a new DeleteAllFavouriteCommand instance.

        Args:
            avourites_manager (FavouritesManager): Manager for handling favourites-related operations.
            Note: There appears to be a typo in the parameter name ('avourites_manager' vs 'favourites_manager').
        """
        self.avourites_manager = avourites_manager

    def execute(self):
        """
        Execute the command to delete all favourite songs.

        Calls the clear_favourites method of the associated favourites manager.
        """
        self.avourites_manager.clear_favourites()


class LoadPlaylistCommand(ICommand):
    """
    Command for loading a playlist.

    Implements the ICommand interface to provide a standard way to handle loading a playlist.
    """

    def __init__(self, playlist_manager: PlaylistManager, parent):
        """
        Initialize a new LoadPlaylistCommand instance.

        Args:
            playlist_manager (PlaylistManager): Manager for handling playlist-related operations.
            parent: The parent widget or controller that contains this command.
        """
        self.playlist_manager = playlist_manager
        self.parent = parent

    def execute(self):
        """
        Execute the command to load a playlist.

        Calls the load_playlist_into_widget method of the associated playlist manager.
        """
        self.playlist_manager.load_playlist_into_widget(self.parent)


class NewPlaylistCommand(ICommand):
    """
    Command for creating a new playlist.

    Implements the ICommand interface to provide a standard way to handle creating a new playlist.
    """

    def __init__(self, playlist_manager: PlaylistManager, parent):
        """
        Initialize a new NewPlaylistCommand instance.

        Args:
            playlist_manager (PlaylistManager): Manager for handling playlist-related operations.
            parent: The parent widget or controller that contains this command.
        """
        self.playlist_manager = playlist_manager
        self.parent = parent

    def execute(self):
        """
        Execute the command to create a new playlist.

        Calls the create_playlist method of the associated playlist manager.
        """
        self.playlist_manager.create_playlist(self.parent)


class DeletePlaylistCommand(ICommand):
    """
    Command for deleting a playlist.

    Implements the ICommand interface to provide a standard way to handle deleting a playlist.
    """

    def __init__(self, playlist_manager: PlaylistManager, parent):
        """
        Initialize a new DeletePlaylistCommand instance.

        Args:
            playlist_manager (PlaylistManager): Manager for handling playlist-related operations.
            parent: The parent widget or controller that contains this command.
        """
        self.playlist_manager = playlist_manager
        self.parent = parent

    def execute(self):
        """
        Execute the command to delete a playlist.

        Calls the remove_playlist method of the associated playlist manager.
        """
        self.playlist_manager.remove_playlist(self.parent)


class DeleteAllPlaylistCommand(ICommand):
    """
    Command for deleting all playlists.

    Implements the ICommand interface to provide a standard way to handle deleting all playlists.
    """

    def __init__(self, playlist_manager: PlaylistManager, parent):
        """
        Initialize a new DeleteAllPlaylistCommand instance.

        Args:
            playlist_manager (PlaylistManager): Manager for handling playlist-related operations.
            parent: The parent widget or controller that contains this command.
        """
        self.playlist_manager = playlist_manager
        self.parent = parent

    def execute(self):
        """
        Execute the command to delete all playlists.

        Calls the remove_all_playlists method of the associated playlist manager.
        """
        self.playlist_manager.remove_all_playlists(self.parent)

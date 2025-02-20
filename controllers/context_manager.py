from dataclasses import dataclass
from PyQt5.QtWidgets import QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from interfaces.context import commands as cmd
from interfaces.context.command_action import CommandAction
from utils import messages as msg


@dataclass
class PlaybackCommands:
    """Container for playback-related commands.

    This dataclass groups together commands related to media playback control,
    including play, pause, next, previous, and stop operations.

    Attributes:
        play: Command for starting playback.
        pause: Command for pausing/resuming playback.
        next: Command for playing next track.
        previous: Command for playing previous track.
        stop: Command for stopping playback.
    """

    play: cmd.PlayCommand
    pause: cmd.PauseCommand
    next: cmd.NextCommand
    previous: cmd.PreviousCommand
    stop: cmd.StopCommand


@dataclass
class FavoriteCommands:
    """Container for favorites-related commands.

    This dataclass groups together commands related to favorites management,
    including adding selected or all songs to favorites.

    Attributes:
        selected_to_favorites: Command for adding selected songs to favorites.
        all_to_favorites: Command for adding all songs to favorites.
    """

    selected_to_favorites: cmd.SelectedToFavouritesCommand
    all_to_favorites: cmd.AllToFavouritesCommand


@dataclass
class PlaylistCommands:
    """Container for playlist-related commands.

    This dataclass groups together commands related to playlist management,
    including adding selected or all songs to playlists.

    Attributes:
        selected_to_playlist: Command for adding selected songs to playlist.
        all_to_playlist: Command for adding all songs to playlist.
    """

    selected_to_playlist: cmd.SelectedToPlaylistCommand
    all_to_playlist: cmd.AllToPlaylistCommand


@dataclass
class PlaylistManagerCommands:
    """Container for playlist management commands.

    This dataclass groups together commands for managing playlists, including
    loading, creating, and deleting playlists.

    Attributes:
        load_playlist: Command for loading selected playlist.
        create_playlist: Command for creating new playlist.
        delete_selected: Command for deleting selected playlist.
        delete_all: Command for deleting all playlists.
    """

    load_playlist: cmd.LoadPlaylistCommand
    create_playlist: cmd.NewPlaylistCommand
    delete_selected: cmd.DeletePlaylistCommand
    delete_all: cmd.DeleteAllPlaylistCommand


@dataclass
class FavouritesManagerCommands:
    """Container for favourites management commands.

    This dataclass groups together commands for managing favorites,
    including deleting selected or all favorite items.

    Attributes:
        delete_selected: Command for deleting selected favourites.
        delete_all: Command for deleting all favourites.
    """

    delete_selected: cmd.DeleteSelectedFavouriteCommand
    delete_all: cmd.DeleteAllFavouriteCommand


class BaseContextMenuManager:
    """Base class for context menu managers.

    Provides common functionality for all context menu managers, including
    methods for creating menu actions and separators.

    Attributes:
        parent: Parent widget containing the context menu.
    """

    def __init__(self, parent):
        """Initialize the base context menu manager.

        Args:
            parent: Parent widget containing the context menu.
        """
        self.parent = parent

    def _create_separator(self):
        """Create a menu separator action.

        Returns:
            QAction: A separator action for visually separating menu items.
        """
        separator = QAction(self.parent)
        separator.setSeparator(True)
        return separator

    def _create_menu_action(self, command, icon_path, message):
        """Create a menu action with the specified parameters.

        Args:
            command: Command to execute when the action is triggered.
            icon_path: Path to the action's icon.
            message: Text to display for the action.

        Returns:
            CommandAction: Created menu action with the specified parameters.
        """
        return CommandAction(QIcon(icon_path), message, self.parent, command)

    def _add_actions_from_list(self, menu, actions):
        """Add multiple actions to menu from a list of action specifications.

        Args:
            menu: Menu widget to add actions to.
            actions: List of tuples (command, icon_path, message) specifying actions.
        """
        for command, icon_path, message in actions:
            action = self._create_menu_action(command, icon_path, message)
            menu.addAction(action)


class SongsListContextMenuManager(BaseContextMenuManager):
    """Manages the context menu for the Songs List.

    Handles setup and management of context menu actions for song playback control
    and adding songs to favourites or playlists.

    Attributes:
        parent: Parent widget containing the context menu.
        playback_commands: Container for playback-related commands.
        favorite_commands: Container for favorites-related commands.
        playlist_commands: Container for playlist-related commands.
    """
    def __init__(self, parent, event_handler, favourites_manager, playlist_manager):
        """Initialize the SongsListContextMenuManager.

        Args:
            parent: Parent widget containing the context menu.
            event_handler: Handler for playback control events.
            favourites_manager: Manager for favourites-related operations.
            playlist_manager: Manager for playlist-related operations.
        """
        super().__init__(parent)
        self._initialize_commands(event_handler, favourites_manager, playlist_manager)
        self.setup_menu()

    def _initialize_commands(self, event_handler, favourites_manager, playlist_manager):
        """Initialize command containers for different operation types.

        Args:
            event_handler: Handler for playback control events.
            favourites_manager: Manager for favourites-related operations.
            playlist_manager: Manager for playlist-related operations.
        """
        self.playback_commands = PlaybackCommands(
            play=cmd.PlayCommand(event_handler),
            pause=cmd.PauseCommand(event_handler),
            next=cmd.NextCommand(event_handler),
            previous=cmd.PreviousCommand(event_handler),
            stop=cmd.StopCommand(event_handler),
        )
        self.favorite_commands = FavoriteCommands(
            selected_to_favorites=cmd.SelectedToFavouritesCommand(favourites_manager),
            all_to_favorites=cmd.AllToFavouritesCommand(favourites_manager),
        )
        self.playlist_commands = PlaylistCommands(
            selected_to_playlist=cmd.SelectedToPlaylistCommand(playlist_manager, self.parent),
            all_to_playlist=cmd.AllToPlaylistCommand(playlist_manager, self.parent),
        )

    def _add_playback_actions(self, menu):
        """Add playback control actions to the context menu.

        Adds actions for play, pause, next, previous, and stop operations.

        Args:
            menu: Menu widget to add actions to.
        """
        actions = [
            (self.playback_commands.play, ":/img/utils/images/pase.png", msg.CTX_PLAY),
            (
                self.playback_commands.pause,
                ":/img/utils/images/play.png",
                msg.CTX_PAUSE,
            ),
            (self.playback_commands.next, ":/img/utils/images/next.png", msg.CTX_NEXT),
            (
                self.playback_commands.previous,
                ":/img/utils/images/pre.png",
                msg.CTX_PREVS,
            ),
            (self.playback_commands.stop, ":/img/utils/images/stop.png", msg.CTX_STOP),
        ]
        self._add_actions_from_list(menu, actions)

    def _add_favorites_actions(self, menu):
        """Add favorites-related actions to the context menu.

        Adds actions for adding selected or all songs to favorites.

        Args:
            menu: Menu widget to add actions to.
        """
        actions = [
            (
                self.favorite_commands.selected_to_favorites,
                ":/img/utils/images/like.png",
                msg.CTX_ADD_TO_FAV,
            ),
            (
                self.favorite_commands.all_to_favorites,
                ":/img/utils/images/like.png",
                msg.CTX_ADD_ALL_TO_FAV,
            ),
        ]
        self._add_actions_from_list(menu, actions)

    def _add_playlist_actions(self, menu):
        """Add playlist-related actions to the context menu.

        Adds actions for adding selected or all songs to playlist.

        Args:
            menu: Menu widget to add actions to.
        """
        actions = [
            (
                self.playlist_commands.selected_to_playlist,
                ":/img/utils/images/MusicListItem.png",
                msg.CTX_ADD_TO_LST,
            ),
            (
                self.playlist_commands.all_to_playlist,
                ":/img/utils/images/MusicListItem.png",
                msg.CTX_ADD_ALL_TO_LST,
            ),
        ]
        self._add_actions_from_list(menu, actions)

    def setup_menu(self):
        """Setup the context menu with all available actions.

        Configures the menu with playback controls, favorites actions,
        and playlist actions, separated by dividers.
        """
        menu = self.parent.loaded_songs_listWidget
        menu.setContextMenuPolicy(Qt.ActionsContextMenu)
        self._add_playback_actions(menu)
        menu.addAction(self._create_separator())
        self._add_favorites_actions(menu)
        menu.addAction(self._create_separator())
        self._add_playlist_actions(menu)


class PlaylistContextMenuManager(BaseContextMenuManager):
    """Manages the context menu for the Playlists tab.

    Handles setup and management of context menu actions for playlist operations
    like loading, creating, and deleting playlists.

    Attributes:
        parent: Parent widget containing the context menu.
        playlist_commands: Container for playlist management commands.
    """

    def __init__(self, parent, playlist_manager):
        """Initialize the PlaylistContextMenuManager.

        Args:
            parent: Parent widget containing the context menu.
            playlist_manager: Manager for playlist-related operations.
        """
        super().__init__(parent)
        self._initialize_commands(playlist_manager)
        self.setup_menu()

    def _initialize_commands(self, playlist_manager):
        """Initialize command container for playlist operations.

        Args:
            playlist_manager: Manager for playlist-related operations.
        """
        self.playlist_commands = PlaylistManagerCommands(
            load_playlist=cmd.LoadPlaylistCommand(playlist_manager, self.parent),
            create_playlist=cmd.NewPlaylistCommand(playlist_manager, self.parent),
            delete_selected=cmd.DeletePlaylistCommand(playlist_manager, self.parent),
            delete_all=cmd.DeleteAllPlaylistCommand(playlist_manager, self.parent),
        )

    def _add_playlist_load_actions(self, menu):
        """Add playlist loading actions to the context menu.

        Adds action for loading a selected playlist.

        Args:
            menu: Menu widget to add actions to.
        """
        action = self._create_menu_action(
            self.playlist_commands.load_playlist,
            ":/img/utils/images/music_list.png",
            msg.CTX_LOAD_LST,
        )
        menu.addAction(action)

    def _add_playlist_creation_actions(self, menu):
        """Add playlist creation actions to the context menu.

        Adds action for creating a new playlist.

        Args:
            menu: Menu widget to add actions to.
        """
        action = self._create_menu_action(
            self.playlist_commands.create_playlist,
            ":/img/utils/images/music_list.png",
            msg.CTX_NEW_LST,
        )
        menu.addAction(action)

    def _add_playlist_deletion_actions(self, menu):
        """Add playlist deletion actions to the context menu.

        Adds actions for deleting selected or all playlists.

        Args:
            menu: Menu widget to add actions to.
        """
        actions = [
            (
                self.playlist_commands.delete_selected,
                ":/img/utils/images/clear.png",
                msg.CTX_DEL_SEL_LST,
            ),
            (
                self.playlist_commands.delete_all,
                ":/img/utils/images/remove.png",
                msg.CTX_DEL_ALL_LST,
            ),
        ]
        self._add_actions_from_list(menu, actions)

    def setup_menu(self):
        """Setup the context menu with all available actions.

        Configures the menu with playlist loading, creation, and deletion actions,
        separated by dividers.
        """
        menu = self.parent.playlists_listWidget
        menu.setContextMenuPolicy(Qt.ActionsContextMenu)
        self._add_playlist_load_actions(menu)
        menu.addAction(self._create_separator())
        self._add_playlist_creation_actions(menu)
        menu.addAction(self._create_separator())
        self._add_playlist_deletion_actions(menu)


class FavouritesContextMenuManager(BaseContextMenuManager):
    """Manages the context menu for the Favourites tab.

    Handles setup and management of context menu actions for favourites operations,
    primarily deletion operations.

    Attributes:
        parent: Parent widget containing the context menu.
        favourites_commands: Container for favourites management commands.
    """

    def __init__(self, parent, favourites_manager):
        """Initialize the FavouritesContextMenuManager.

        Args:
            parent: Parent widget containing the context menu.
            favourites_manager: Manager for favourites-related operations.
        """
        super().__init__(parent)
        self._initialize_commands(favourites_manager)
        self.setup_menu()

    def _initialize_commands(self, favourites_manager):
        """Initialize command container for favourites operations.

        Args:
            favourites_manager: Manager for favourites-related operations.
        """
        self.favourites_commands = FavouritesManagerCommands(
            delete_selected=cmd.DeleteSelectedFavouriteCommand(favourites_manager),
            delete_all=cmd.DeleteAllFavouriteCommand(favourites_manager),
        )

    def setup_menu(self):
        """Setup the context menu with all available actions.

        Configures the menu with favourites deletion actions.
        """
        menu = self.parent.favourites_listWidget
        menu.setContextMenuPolicy(Qt.ActionsContextMenu)
        actions = [
            (
                self.favourites_commands.delete_selected,
                ":/img/utils/images/clear.png",
                msg.CTX_DEL_SEL,
            ),
            (
                self.favourites_commands.delete_all,
                ":/img/utils/images/remove.png",
                msg.CTX_DEL_ALL,
            ),
        ]
        self._add_actions_from_list(menu, actions)


class ContextMenuManager:
    """Main manager class that coordinates all context menus in the application.

    Creates and coordinates the context menu managers for different parts of the
    application: favourites list, playlist list, and songs list.

    Attributes:
        parent: Parent widget containing all list widgets.
        event_handler: Handler for playback control events.
        favourites_manager: Manager for favourites-related operations.
        playlist_manager: Manager for playlist-related operations.
        fav_menu: Instance of FavouritesContextMenuManager.
        playlist_menu: Instance of PlaylistContextMenuManager.
        songs_menu: Instance of SongsListContextMenuManager.
    """

    def __init__(self, parent, event_handler, favourites_manager, playlist_manager):
        """Initialize the main ContextMenuManager.

        Args:
            parent: Parent widget containing all list widgets.
            event_handler: Handler for playback control events.
            favourites_manager: Manager for favourites-related operations.
            playlist_manager: Manager for playlist-related operations.
        """
        self.parent = parent
        self.event_handler = event_handler
        self.favourites_manager = favourites_manager
        self.playlist_manager = playlist_manager
        self.setup_all_menus()

    def setup_all_menus(self):
        """Setup the context menu with all available actions.

        Configures the menu with playback, favourites and playlists actions.
        """
        self.fav_menu = FavouritesContextMenuManager(
            self.parent, self.favourites_manager
        )
        self.playlist_menu = PlaylistContextMenuManager(
            self.parent, self.playlist_manager
        )
        self.songs_menu = SongsListContextMenuManager(
            self.parent,
            self.event_handler,
            self.favourites_manager,
            self.playlist_manager,
        )

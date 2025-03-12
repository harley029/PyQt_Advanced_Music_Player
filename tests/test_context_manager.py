# pylint: disable=redefined-outer-name
# pylint: disable=duplicate-code

import sys

from unittest.mock import MagicMock, patch
import pytest

from PyQt5.QtWidgets import QApplication, QListWidget, QAction, QWidget
from PyQt5.QtCore import Qt

from controllers.context_manager import (
    BaseContextMenuManager,
    SongsListContextMenuManager,
    PlaylistContextMenuManager,
    FavouritesContextMenuManager,
    ContextMenuManager,
    PlaybackCommands,
    FavoriteCommands,
    PlaylistCommands,
    PlaylistManagerCommands,
    FavouritesManagerCommands,
)
from interfaces.context import commands as cmd
from interfaces.context.command_action import CommandAction


@pytest.fixture
def app():
    """
    Fixture providing a QApplication instance for testing.
    
    This fixture ensures that a QApplication instance exists, which is required for
    creating and interacting with Qt widgets in tests. If an instance already exists,
    it returns that instance; otherwise, it creates a new one.
    
    Returns:
        QApplication: An instance of QApplication for use in tests.
    """
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    yield application


@pytest.fixture
def parent_widget():
    """
    Fixture providing a parent widget with necessary list widgets.
    
    Creates a QWidget with three QListWidget attributes commonly used in the application:
    - loaded_songs_listWidget: For displaying loaded songs
    - playlists_listWidget: For displaying available playlists
    - favourites_listWidget: For displaying favourite songs
    
    Returns:
        QWidget: A parent widget with three list widget attributes.
    """
    parent = QWidget()
    parent.loaded_songs_listWidget = QListWidget()
    parent.playlists_listWidget = QListWidget()
    parent.favourites_listWidget = QListWidget()
    return parent


@pytest.fixture
def event_handler():
    """
    Fixture providing a mock event handler for testing.
    
    This mock object simulates the behavior of an event handler that processes
    playback events like play, pause, next, etc.
    
    Returns:
        MagicMock: A mock object that can be used as an event handler.
    """
    return MagicMock()


@pytest.fixture
def favourites_manager():
    """
    Fixture providing a mock favourites manager for testing.
    
    This mock object simulates the behavior of a manager responsible for handling
    favourite songs operations like adding, removing, etc.
    
    Returns:
        MagicMock: A mock object that can be used as a favourites manager.
    """
    return MagicMock()


@pytest.fixture
def playlist_manager():
    """
    Fixture providing a mock playlist manager for testing.
    
    This mock object simulates the behavior of a manager responsible for handling
    playlist operations like creation, loading, deletion, etc.
    
    Returns:
        MagicMock: A mock object that can be used as a playlist manager.
    """
    return MagicMock()


class TestBaseContextMenuManager:

    def test_init(self, parent_widget):
        """
        Test initialization of BaseContextMenuManager.
        
        Verifies that the BaseContextMenuManager constructor correctly sets the parent widget.
        
        Args:
            parent_widget (QWidget): The fixture providing a parent widget.
            
        Asserts:
            The parent attribute of the manager is set to the provided parent widget.
        """
        base_manager = BaseContextMenuManager(parent_widget)
        assert base_manager.parent == parent_widget

    def test_create_separator(self, parent_widget):
        """
        Test creating a separator action.
        
        Verifies that the _create_separator method creates a valid separator action.
        
        Args:
            parent_widget (QWidget): The fixture providing a parent widget.
            
        Asserts:
            The returned object is a QAction.
            The QAction is correctly configured as a separator.
        """
        base_manager = BaseContextMenuManager(parent_widget)
        separator = base_manager._create_separator()

        assert isinstance(separator, QAction)
        assert separator.isSeparator()

    def test_create_menu_action(self, parent_widget):
        """
        Test creating a menu action.
        
        Verifies that the _create_menu_action method creates a valid CommandAction with
        appropriate text, icon, and parent.
        
        Args:
            parent_widget (QWidget): The fixture providing a parent widget.
            
        Asserts:
            The returned object is a CommandAction.
            The CommandAction has the specified text.
            The CommandAction has the correct parent widget.
        """
        base_manager = BaseContextMenuManager(parent_widget)
        mock_command = MagicMock()

        with patch("PyQt5.QtGui.QIcon", return_value=MagicMock()):
            action = base_manager._create_menu_action(
                mock_command, "dummy_path", "Test Action"
            )

        assert isinstance(action, CommandAction)
        assert action.text() == "Test Action"
        assert action.parent() == parent_widget

    def test_add_actions_from_list(self, parent_widget):
        """
        Test adding multiple actions to a menu.
        
        Verifies that the _add_actions_from_list method correctly creates and adds
        multiple actions to the specified menu.
        
        Args:
            parent_widget (QWidget): The fixture providing a parent widget.
            
        Asserts:
            _create_menu_action is called twice (once for each action).
            addAction is called twice on the menu (once for each action).
        """
        base_manager = BaseContextMenuManager(parent_widget)
        mock_menu = MagicMock()
        mock_command1 = MagicMock()
        mock_command2 = MagicMock()

        with patch.object(base_manager, "_create_menu_action") as mock_create:
            mock_create.side_effect = [
                QAction("Action1", parent_widget),
                QAction("Action2", parent_widget),
            ]

            base_manager._add_actions_from_list(
                mock_menu,
                [
                    (mock_command1, "path1", "Action1"),
                    (mock_command2, "path2", "Action2"),
                ],
            )

        assert mock_create.call_count == 2
        assert mock_menu.addAction.call_count == 2


class TestSongsListContextMenuManager:

    def test_init(
        self, parent_widget, event_handler, favourites_manager, playlist_manager
    ):
        """
        Test initialization of SongsListContextMenuManager.
        
        Verifies that the SongsListContextMenuManager constructor correctly initializes
        all command containers and their respective commands.
        
        Args:
            parent_widget (QWidget): The fixture providing a parent widget.
            event_handler (MagicMock): The fixture providing a mock event handler.
            favourites_manager (MagicMock): The fixture providing a mock favourites manager.
            playlist_manager (MagicMock): The fixture providing a mock playlist manager.
            
        Asserts:
            Various command containers and individual commands are correctly initialized.
        """
        with patch.object(SongsListContextMenuManager, "setup_menu"):
            manager = SongsListContextMenuManager(
                parent_widget, event_handler, favourites_manager, playlist_manager
            )

            assert isinstance(manager.playback_commands, PlaybackCommands)
            assert isinstance(manager.favorite_commands, FavoriteCommands)
            assert isinstance(manager.playlist_commands, PlaylistCommands)
            assert manager.playback_commands.play.event_handler == event_handler
            assert isinstance(
                manager.favorite_commands.selected_to_favorites,
                cmd.SelectedToFavouritesCommand,
            )
            assert isinstance(
                manager.playlist_commands.selected_to_playlist,
                cmd.SelectedToPlaylistCommand,
            )

    def test_setup_menu(
        self, parent_widget, event_handler, favourites_manager, playlist_manager
    ):
        """
        Test setup_menu configures the context menu with all required actions.
        
        Verifies that the setup_menu method correctly configures the loaded_songs_listWidget
        with the appropriate context menu policy and adds the necessary action groups.
        
        Args:
            parent_widget (QWidget): The fixture providing a parent widget.
            event_handler (MagicMock): The fixture providing a mock event handler.
            favourites_manager (MagicMock): The fixture providing a mock favourites manager.
            playlist_manager (MagicMock): The fixture providing a mock playlist manager.
            
        Asserts:
            The loaded_songs_listWidget has the ActionsContextMenu policy.
            The methods to add various action groups are called exactly once each.
        """
        with patch.object(
            SongsListContextMenuManager, "_add_playback_actions"
        ), patch.object(
            SongsListContextMenuManager, "_add_favorites_actions"
        ), patch.object(
            SongsListContextMenuManager, "_add_playlist_actions"
        ), patch.object(
            SongsListContextMenuManager, "_create_separator", return_value=QAction()
        ):

            manager = SongsListContextMenuManager(
                parent_widget, event_handler, favourites_manager, playlist_manager
            )

            assert (
                parent_widget.loaded_songs_listWidget.contextMenuPolicy()
                == Qt.ActionsContextMenu
            )

            manager._add_playback_actions.assert_called_once()
            manager._add_favorites_actions.assert_called_once()
            manager._add_playlist_actions.assert_called_once()

    def test_add_playback_actions(
        self, parent_widget, event_handler, favourites_manager, playlist_manager
    ):
        """
        Test adding playback actions to the menu.
        
        Verifies that the _add_playback_actions method correctly adds the playback actions
        to the context menu.
        
        Args:
            parent_widget (QWidget): The fixture providing a parent widget.
            event_handler (MagicMock): The fixture providing a mock event handler.
            favourites_manager (MagicMock): The fixture providing a mock favourites manager.
            playlist_manager (MagicMock): The fixture providing a mock playlist manager.
            
        Asserts:
            _add_actions_from_list is called exactly once.
            The actions list contains exactly 5 actions (Play, Pause, Next, Previous, Stop).
        """
        with patch.object(SongsListContextMenuManager, "setup_menu"):
            manager = SongsListContextMenuManager(
                parent_widget, event_handler, favourites_manager, playlist_manager
            )

        with patch.object(manager, "_add_actions_from_list") as mock_add:
            mock_menu = MagicMock()
            manager._add_playback_actions(mock_menu)

            mock_add.assert_called_once()
            actions_list = mock_add.call_args[0][1]
            assert len(actions_list) == 5  # Play, Pause, Next, Previous, Stop

    def test_add_favorites_actions(
        self, parent_widget, event_handler, favourites_manager, playlist_manager
    ):
        """
        Test adding favorites actions to the menu.
        
        Verifies that the _add_favorites_actions method correctly adds the favorites actions
        to the context menu.
        
        Args:
            parent_widget (QWidget): The fixture providing a parent widget.
            event_handler (MagicMock): The fixture providing a mock event handler.
            favourites_manager (MagicMock): The fixture providing a mock favourites manager.
            playlist_manager (MagicMock): The fixture providing a mock playlist manager.
            
        Asserts:
            _add_actions_from_list is called exactly once.
            The actions list contains exactly 2 actions (Selected to favorites, All to favorites).
        """
        with patch.object(SongsListContextMenuManager, "setup_menu"):
            manager = SongsListContextMenuManager(
                parent_widget, event_handler, favourites_manager, playlist_manager
            )

        with patch.object(manager, "_add_actions_from_list") as mock_add:
            mock_menu = MagicMock()
            manager._add_favorites_actions(mock_menu)
            mock_add.assert_called_once()
            actions_list = mock_add.call_args[0][1]
            assert len(actions_list) == 2  # Selected to favorites, All to favorites

    def test_add_playlist_actions(
        self, parent_widget, event_handler, favourites_manager, playlist_manager
    ):
        """
        Test adding playlist actions to the menu.
        
        Verifies that the _add_playlist_actions method correctly adds the playlist actions
        to the context menu.
        
        Args:
            parent_widget (QWidget): The fixture providing a parent widget.
            event_handler (MagicMock): The fixture providing a mock event handler.
            favourites_manager (MagicMock): The fixture providing a mock favourites manager.
            playlist_manager (MagicMock): The fixture providing a mock playlist manager.
            
        Asserts:
            _add_actions_from_list is called exactly once.
            The actions list contains exactly 2 actions (Selected to playlist, All to playlist).
        """
        with patch.object(SongsListContextMenuManager, "setup_menu"):
            manager = SongsListContextMenuManager(
                parent_widget, event_handler, favourites_manager, playlist_manager
            )
        with patch.object(manager, "_add_actions_from_list") as mock_add:
            mock_menu = MagicMock()
            manager._add_playlist_actions(mock_menu)
            mock_add.assert_called_once()
            actions_list = mock_add.call_args[0][1]
            assert len(actions_list) == 2  # Selected to playlist, All to playlist


class TestPlaylistContextMenuManager:

    def test_init(self, parent_widget, playlist_manager):
        """
        Test initialization of PlaylistContextMenuManager.

        Verifies that the PlaylistContextMenuManager constructor correctly initializes
        the playlist commands container and its commands.

        Args:
            parent_widget (QWidget): The fixture providing a parent widget.
            playlist_manager (MagicMock): The fixture providing a mock playlist manager.

        Asserts:
            The playlist_commands attribute is correctly initialized as a PlaylistManagerCommands.
            The load_playlist command is correctly initialized as a LoadPlaylistCommand.
        """
        with patch.object(PlaylistContextMenuManager, "setup_menu"):
            manager = PlaylistContextMenuManager(parent_widget, playlist_manager)

            assert isinstance(manager.playlist_commands, PlaylistManagerCommands)
            assert isinstance(
                manager.playlist_commands.load_playlist, cmd.LoadPlaylistCommand
            )

    def test_setup_menu(self, parent_widget, playlist_manager):
        """
        Test setup_menu configures the context menu with all required actions.

        Verifies that the setup_menu method correctly configures the playlists_listWidget
        with the appropriate context menu policy and adds the necessary action groups.

        Args:
            parent_widget (QWidget): The fixture providing a parent widget.
            playlist_manager (MagicMock): The fixture providing a mock playlist manager.

        Asserts:
            The playlists_listWidget has the ActionsContextMenu policy.
            The methods to add various action groups are called exactly once each.
        """
        with patch.object(
            PlaylistContextMenuManager, "_add_playlist_load_actions"
        ), patch.object(
            PlaylistContextMenuManager, "_add_playlist_creation_actions"
        ), patch.object(
            PlaylistContextMenuManager, "_add_playlist_deletion_actions"
        ), patch.object(
            PlaylistContextMenuManager, "_create_separator", return_value=QAction()
        ):

            manager = PlaylistContextMenuManager(parent_widget, playlist_manager)

            assert (
                parent_widget.playlists_listWidget.contextMenuPolicy()
                == Qt.ActionsContextMenu
            )

            manager._add_playlist_load_actions.assert_called_once()
            manager._add_playlist_creation_actions.assert_called_once()
            manager._add_playlist_deletion_actions.assert_called_once()

    def test_add_playlist_load_actions(self, parent_widget, playlist_manager):
        """
        Test adding playlist load actions to the menu.

        Verifies that the _add_playlist_load_actions method correctly creates and adds
        a playlist load action to the menu.

        Args:
            parent_widget (QWidget): The fixture providing a parent widget.
            playlist_manager (MagicMock): The fixture providing a mock playlist manager.

        Asserts:
            _create_menu_action is called exactly once.
            addAction is called exactly once on the menu.
        """
        with patch.object(PlaylistContextMenuManager, "setup_menu"):
            manager = PlaylistContextMenuManager(parent_widget, playlist_manager)

        with patch.object(
            manager, "_create_menu_action", return_value=QAction()
        ) as mock_create:
            mock_menu = MagicMock()
            manager._add_playlist_load_actions(mock_menu)

            mock_create.assert_called_once()
            assert mock_menu.addAction.call_count == 1

    def test_add_playlist_creation_actions(self, parent_widget, playlist_manager):
        """
        Test adding playlist creation actions to the menu.

        Verifies that the _add_playlist_creation_actions method correctly creates and adds
        a playlist creation action to the menu.

        Args:
            parent_widget (QWidget): The fixture providing a parent widget.
            playlist_manager (MagicMock): The fixture providing a mock playlist manager.

        Asserts:
            _create_menu_action is called exactly once.
            addAction is called exactly once on the menu.
        """
        with patch.object(PlaylistContextMenuManager, "setup_menu"):
            manager = PlaylistContextMenuManager(parent_widget, playlist_manager)

        with patch.object(
            manager, "_create_menu_action", return_value=QAction()
        ) as mock_create:
            mock_menu = MagicMock()
            manager._add_playlist_creation_actions(mock_menu)

            mock_create.assert_called_once()
            assert mock_menu.addAction.call_count == 1

    def test_add_playlist_deletion_actions(self, parent_widget, playlist_manager):
        """
        Test adding playlist deletion actions to the menu.

        Verifies that the _add_playlist_deletion_actions method correctly adds the
        playlist deletion actions to the menu.

        Args:
            parent_widget (QWidget): The fixture providing a parent widget.
            playlist_manager (MagicMock): The fixture providing a mock playlist manager.

        Asserts:
            _add_actions_from_list is called exactly once.
            The actions list contains exactly 2 actions (Delete selected, Delete all).
        """
        with patch.object(PlaylistContextMenuManager, "setup_menu"):
            manager = PlaylistContextMenuManager(parent_widget, playlist_manager)

        with patch.object(manager, "_add_actions_from_list") as mock_add:
            mock_menu = MagicMock()
            manager._add_playlist_deletion_actions(mock_menu)
            mock_add.assert_called_once()
            actions_list = mock_add.call_args[0][1]
            assert len(actions_list) == 2  # Delete selected, Delete all


class TestFavouritesContextMenuManager:

    def test_init(self, parent_widget, favourites_manager):
        """
        Test initialization of FavouritesContextMenuManager.

        Verifies that the FavouritesContextMenuManager constructor correctly initializes
        the favourites commands container and its commands.

        Args:
            parent_widget (QWidget): The fixture providing a parent widget.
            favourites_manager (MagicMock): The fixture providing a mock favourites manager.

        Asserts:
            The favourites_commands attribute is correctly initialized as a FavouritesManagerCommands.
            The delete_selected command is correctly initialized as a DeleteSelectedFavouriteCommand.
        """
        with patch.object(FavouritesContextMenuManager, "setup_menu"):
            manager = FavouritesContextMenuManager(parent_widget, favourites_manager)

            assert isinstance(manager.favourites_commands, FavouritesManagerCommands)
            assert isinstance(
                manager.favourites_commands.delete_selected,
                cmd.DeleteSelectedFavouriteCommand,
            )

    def test_setup_menu(self, parent_widget, favourites_manager):
        """
        Test setup_menu configures the context menu with all required actions.

        Verifies that the setup_menu method correctly configures the favourites_listWidget
        with the appropriate context menu policy and adds the necessary action groups.

        Args:
            parent_widget (QWidget): The fixture providing a parent widget.
            favourites_manager (MagicMock): The fixture providing a mock favourites manager.

        Asserts:
            The favourites_listWidget has the ActionsContextMenu policy.
            _add_actions_from_list is called exactly once.
            The actions list contains exactly 2 actions (Delete selected, Delete all).
        """
        with patch.object(
            FavouritesContextMenuManager, "_add_actions_from_list"
        ) as mock_add:
            manager = FavouritesContextMenuManager(parent_widget, favourites_manager)

            assert (
                parent_widget.favourites_listWidget.contextMenuPolicy()
                == Qt.ActionsContextMenu
            )

            mock_add.assert_called_once()
            actions_list = mock_add.call_args[0][1]
            assert len(actions_list) == 2  # Delete selected, Delete all


class TestContextMenuManager:

    def test_init(
        self, parent_widget, event_handler, favourites_manager, playlist_manager
    ):
        """
        Test initialization of ContextMenuManager.

        Verifies that the ContextMenuManager constructor correctly sets all the
        required attributes.

        Args:
            parent_widget (QWidget): The fixture providing a parent widget.
            event_handler (MagicMock): The fixture providing a mock event handler.
            favourites_manager (MagicMock): The fixture providing a mock favourites manager.
            playlist_manager (MagicMock): The fixture providing a mock playlist manager.

        Asserts:
            All attributes (parent, event_handler, favourites_manager, playlist_manager)
            are correctly set.
        """
        with patch.object(ContextMenuManager, "setup_all_menus"):
            manager = ContextMenuManager(
                parent_widget, event_handler, favourites_manager, playlist_manager
            )

            assert manager.parent == parent_widget
            assert manager.event_handler == event_handler
            assert manager.favourites_manager == favourites_manager
            assert manager.playlist_manager == playlist_manager

    def test_setup_all_menus(
        self, parent_widget, event_handler, favourites_manager, playlist_manager
    ):
        """
        Test setup_all_menus creates all sub-managers correctly.

        Verifies that the setup_all_menus method correctly initializes all three
        context menu managers with the appropriate parameters.

        Args:
            parent_widget (QWidget): The fixture providing a parent widget.
            event_handler (MagicMock): The fixture providing a mock event handler.
            favourites_manager (MagicMock): The fixture providing a mock favourites manager.
            playlist_manager (MagicMock): The fixture providing a mock playlist manager.

        Asserts:
            All three manager classes are instantiated with the correct parameters.
            All three manager attributes (fav_menu, playlist_menu, songs_menu) are set
            to the appropriate manager instances.
        """
        with patch(
            "controllers.context_manager.FavouritesContextMenuManager",
            return_value=MagicMock(),
        ) as mock_fav_class, patch(
            "controllers.context_manager.PlaylistContextMenuManager",
            return_value=MagicMock(),
        ) as mock_playlist_class, patch(
            "controllers.context_manager.SongsListContextMenuManager",
            return_value=MagicMock(),
        ) as mock_songs_class:

            manager = ContextMenuManager(
                parent_widget, event_handler, favourites_manager, playlist_manager
            )

            mock_fav_class.assert_called_once_with(parent_widget, favourites_manager)
            mock_playlist_class.assert_called_once_with(parent_widget, playlist_manager)
            mock_songs_class.assert_called_once_with(
                parent_widget, event_handler, favourites_manager, playlist_manager
            )

            assert manager.fav_menu == mock_fav_class.return_value
            assert manager.playlist_menu == mock_playlist_class.return_value
            assert manager.songs_menu == mock_songs_class.return_value


class TestCommandContainers:

    def test_playback_commands(self, event_handler):
        """
        Test PlaybackCommands dataclass structure.

        Verifies that the PlaybackCommands dataclass correctly initializes all
        playback-related commands with the event handler.

        Args:
            event_handler (MagicMock): The fixture providing a mock event handler.

        Asserts:
            All commands (play, pause, next, previous, stop) are initialized with
            the correct command types.
            The event_handler is correctly passed to the Play command.
        """
        commands = PlaybackCommands(
            play=cmd.PlayCommand(event_handler),
            pause=cmd.PauseCommand(event_handler),
            next=cmd.NextCommand(event_handler),
            previous=cmd.PreviousCommand(event_handler),
            stop=cmd.StopCommand(event_handler),
        )

        assert isinstance(commands.play, cmd.PlayCommand)
        assert isinstance(commands.pause, cmd.PauseCommand)
        assert isinstance(commands.next, cmd.NextCommand)
        assert isinstance(commands.previous, cmd.PreviousCommand)
        assert isinstance(commands.stop, cmd.StopCommand)

        assert commands.play.event_handler == event_handler

    def test_favorite_commands(self, favourites_manager):
        """
        Test FavoriteCommands dataclass structure.

        Verifies that the FavoriteCommands dataclass correctly initializes all
        favorite-related commands with the favourites manager.

        Args:
            favourites_manager (MagicMock): The fixture providing a mock favourites manager.

        Asserts:
            All commands (selected_to_favorites, all_to_favorites) are initialized with
            the correct command types.
        """
        commands = FavoriteCommands(
            selected_to_favorites=cmd.SelectedToFavouritesCommand(favourites_manager),
            all_to_favorites=cmd.AllToFavouritesCommand(favourites_manager),
        )

        assert isinstance(
            commands.selected_to_favorites, cmd.SelectedToFavouritesCommand
        )
        assert isinstance(commands.all_to_favorites, cmd.AllToFavouritesCommand)

    def test_playlist_commands(self, playlist_manager, parent_widget):
        """
        Test PlaylistCommands dataclass structure.

        Verifies that the PlaylistCommands dataclass correctly initializes all
        playlist-related commands with the playlist manager and parent widget.

        Args:
            playlist_manager (MagicMock): The fixture providing a mock playlist manager.
            parent_widget (QWidget): The fixture providing a parent widget.

        Asserts:
            All commands (selected_to_playlist, all_to_playlist) are initialized with
            the correct command types.
        """
        commands = PlaylistCommands(
            selected_to_playlist=cmd.SelectedToPlaylistCommand(
                playlist_manager, parent_widget
            ),
            all_to_playlist=cmd.AllToPlaylistCommand(playlist_manager, parent_widget),
        )

        assert isinstance(commands.selected_to_playlist, cmd.SelectedToPlaylistCommand)
        assert isinstance(commands.all_to_playlist, cmd.AllToPlaylistCommand)

    def test_playlist_manager_commands(self, playlist_manager, parent_widget):
        """
        Test PlaylistManagerCommands dataclass structure.

        Verifies that the PlaylistManagerCommands dataclass correctly initializes all
        playlist manager-related commands with the playlist manager and parent widget.

        Args:
            playlist_manager (MagicMock): The fixture providing a mock playlist manager.
            parent_widget (QWidget): The fixture providing a parent widget.

        Asserts:
            All commands (load_playlist, create_playlist, delete_selected, delete_all)
            are initialized with the correct command types.
        """
        commands = PlaylistManagerCommands(
            load_playlist=cmd.LoadPlaylistCommand(playlist_manager, parent_widget),
            create_playlist=cmd.NewPlaylistCommand(playlist_manager, parent_widget),
            delete_selected=cmd.DeletePlaylistCommand(playlist_manager, parent_widget),
            delete_all=cmd.DeleteAllPlaylistCommand(playlist_manager, parent_widget),
        )

        assert isinstance(commands.load_playlist, cmd.LoadPlaylistCommand)
        assert isinstance(commands.create_playlist, cmd.NewPlaylistCommand)
        assert isinstance(commands.delete_selected, cmd.DeletePlaylistCommand)
        assert isinstance(commands.delete_all, cmd.DeleteAllPlaylistCommand)

    def test_favourites_manager_commands(self, favourites_manager):
        """
        Test FavouritesManagerCommands dataclass structure.

        Verifies that the FavouritesManagerCommands dataclass correctly initializes all
        favourites manager-related commands with the favourites manager.

        Args:
            favourites_manager (MagicMock): The fixture providing a mock favourites manager.

        Asserts:
            All commands (delete_selected, delete_all) are initialized with the correct
            command types.
        """
        commands = FavouritesManagerCommands(
            delete_selected=cmd.DeleteSelectedFavouriteCommand(favourites_manager),
            delete_all=cmd.DeleteAllFavouriteCommand(favourites_manager),
        )

        assert isinstance(commands.delete_selected, cmd.DeleteSelectedFavouriteCommand)
        assert isinstance(commands.delete_all, cmd.DeleteAllFavouriteCommand)

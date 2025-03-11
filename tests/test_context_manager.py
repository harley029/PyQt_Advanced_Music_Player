# pylint: disable=redefined-outer-name
import sys
from unittest.mock import MagicMock, patch
import pytest
from PyQt5.QtWidgets import QApplication, QListWidget, QAction, QWidget
from PyQt5.QtCore import Qt

# Use the correct import path that matches the structure of the actual codebase
# The errors suggest the module might be in a different location
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
    """Fixture providing a QApplication instance."""
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    yield application


@pytest.fixture
def parent_widget():
    """Fixture providing a parent widget with list widgets."""
    parent = QWidget()
    parent.loaded_songs_listWidget = QListWidget()
    parent.playlists_listWidget = QListWidget()
    parent.favourites_listWidget = QListWidget()
    return parent


@pytest.fixture
def event_handler():
    """Fixture providing a mock event handler."""
    return MagicMock()


@pytest.fixture
def favourites_manager():
    """Fixture providing a mock favourites manager."""
    return MagicMock()


@pytest.fixture
def playlist_manager():
    """Fixture providing a mock playlist manager."""
    return MagicMock()


class TestBaseContextMenuManager:

    def test_init(self, parent_widget):
        """Test initialization of BaseContextMenuManager."""
        base_manager = BaseContextMenuManager(parent_widget)
        assert base_manager.parent == parent_widget

    def test_create_separator(self, parent_widget):
        """Test creating a separator action."""
        base_manager = BaseContextMenuManager(parent_widget)
        separator = base_manager._create_separator()

        assert isinstance(separator, QAction)
        assert separator.isSeparator()

    def test_create_menu_action(self, parent_widget):
        """Test creating a menu action."""
        base_manager = BaseContextMenuManager(parent_widget)
        mock_command = MagicMock()

        # Using a mock for QIcon to avoid file system dependency
        with patch("PyQt5.QtGui.QIcon", return_value=MagicMock()):
            action = base_manager._create_menu_action(
                mock_command, "dummy_path", "Test Action"
            )

        assert isinstance(action, CommandAction)
        assert action.text() == "Test Action"
        assert action.parent() == parent_widget

    def test_add_actions_from_list(self, parent_widget):
        """Test adding multiple actions to a menu."""
        base_manager = BaseContextMenuManager(parent_widget)
        mock_menu = MagicMock()
        mock_command1 = MagicMock()
        mock_command2 = MagicMock()

        # Mock the _create_menu_action method to avoid dealing with icons
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

        # Verify _create_menu_action was called twice with correct arguments
        assert mock_create.call_count == 2
        # Verify addAction was called twice on the menu
        assert mock_menu.addAction.call_count == 2


class TestSongsListContextMenuManager:

    def test_init(
        self, parent_widget, event_handler, favourites_manager, playlist_manager
    ):
        """Test initialization of SongsListContextMenuManager."""
        with patch.object(SongsListContextMenuManager, "setup_menu"):
            manager = SongsListContextMenuManager(
                parent_widget, event_handler, favourites_manager, playlist_manager
            )

            assert isinstance(manager.playback_commands, PlaybackCommands)
            assert isinstance(manager.favorite_commands, FavoriteCommands)
            assert isinstance(manager.playlist_commands, PlaylistCommands)

            # Verify command instances were created with correct dependencies
            assert manager.playback_commands.play.event_handler == event_handler
            # No need to check attributes that don't exist in the actual code
            # Just check the instance types are correct
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
        """Test setup_menu configures the context menu with all required actions."""
        # Mock all the _add_* methods to avoid dealing with actual UI setup
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

            # Verify context menu policy is set correctly
            assert (
                parent_widget.loaded_songs_listWidget.contextMenuPolicy()
                == Qt.ActionsContextMenu
            )

            # Verify all add methods were called once
            manager._add_playback_actions.assert_called_once()
            manager._add_favorites_actions.assert_called_once()
            manager._add_playlist_actions.assert_called_once()

    def test_add_playback_actions(
        self, parent_widget, event_handler, favourites_manager, playlist_manager
    ):
        """Test adding playback actions to the menu."""
        with patch.object(SongsListContextMenuManager, "setup_menu"):
            manager = SongsListContextMenuManager(
                parent_widget, event_handler, favourites_manager, playlist_manager
            )

        # Mock the _add_actions_from_list method
        with patch.object(manager, "_add_actions_from_list") as mock_add:
            mock_menu = MagicMock()
            manager._add_playback_actions(mock_menu)

            # Verify _add_actions_from_list was called with 5 playback actions
            mock_add.assert_called_once()
            actions_list = mock_add.call_args[0][1]
            assert len(actions_list) == 5  # Play, Pause, Next, Previous, Stop

    def test_add_favorites_actions(
        self, parent_widget, event_handler, favourites_manager, playlist_manager
    ):
        """Test adding favorites actions to the menu."""
        with patch.object(SongsListContextMenuManager, "setup_menu"):
            manager = SongsListContextMenuManager(
                parent_widget, event_handler, favourites_manager, playlist_manager
            )

        # Mock the _add_actions_from_list method
        with patch.object(manager, "_add_actions_from_list") as mock_add:
            mock_menu = MagicMock()
            manager._add_favorites_actions(mock_menu)

            # Verify _add_actions_from_list was called with 2 favorites actions
            mock_add.assert_called_once()
            actions_list = mock_add.call_args[0][1]
            assert len(actions_list) == 2  # Selected to favorites, All to favorites

    def test_add_playlist_actions(
        self, parent_widget, event_handler, favourites_manager, playlist_manager
    ):
        """Test adding playlist actions to the menu."""
        with patch.object(SongsListContextMenuManager, "setup_menu"):
            manager = SongsListContextMenuManager(
                parent_widget, event_handler, favourites_manager, playlist_manager
            )

        # Mock the _add_actions_from_list method
        with patch.object(manager, "_add_actions_from_list") as mock_add:
            mock_menu = MagicMock()
            manager._add_playlist_actions(mock_menu)

            # Verify _add_actions_from_list was called with 2 playlist actions
            mock_add.assert_called_once()
            actions_list = mock_add.call_args[0][1]
            assert len(actions_list) == 2  # Selected to playlist, All to playlist


class TestPlaylistContextMenuManager:

    def test_init(self, parent_widget, playlist_manager):
        """Test initialization of PlaylistContextMenuManager."""
        with patch.object(PlaylistContextMenuManager, "setup_menu"):
            manager = PlaylistContextMenuManager(parent_widget, playlist_manager)

            assert isinstance(manager.playlist_commands, PlaylistManagerCommands)
            # Verify command instances were created with correct types
            assert isinstance(
                manager.playlist_commands.load_playlist, cmd.LoadPlaylistCommand
            )

    def test_setup_menu(self, parent_widget, playlist_manager):
        """Test setup_menu configures the context menu with all required actions."""
        # Mock all the _add_* methods to avoid dealing with actual UI setup
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

            # Verify context menu policy is set correctly
            assert (
                parent_widget.playlists_listWidget.contextMenuPolicy()
                == Qt.ActionsContextMenu
            )

            # Verify all add methods were called once
            manager._add_playlist_load_actions.assert_called_once()
            manager._add_playlist_creation_actions.assert_called_once()
            manager._add_playlist_deletion_actions.assert_called_once()

    def test_add_playlist_load_actions(self, parent_widget, playlist_manager):
        """Test adding playlist load actions to the menu."""
        with patch.object(PlaylistContextMenuManager, "setup_menu"):
            manager = PlaylistContextMenuManager(parent_widget, playlist_manager)

        # Mock the _create_menu_action method
        with patch.object(
            manager, "_create_menu_action", return_value=QAction()
        ) as mock_create:
            mock_menu = MagicMock()
            manager._add_playlist_load_actions(mock_menu)

            # Verify _create_menu_action was called once
            mock_create.assert_called_once()
            # Verify addAction was called once on the menu
            assert mock_menu.addAction.call_count == 1

    def test_add_playlist_creation_actions(self, parent_widget, playlist_manager):
        """Test adding playlist creation actions to the menu."""
        with patch.object(PlaylistContextMenuManager, "setup_menu"):
            manager = PlaylistContextMenuManager(parent_widget, playlist_manager)

        # Mock the _create_menu_action method
        with patch.object(
            manager, "_create_menu_action", return_value=QAction()
        ) as mock_create:
            mock_menu = MagicMock()
            manager._add_playlist_creation_actions(mock_menu)

            # Verify _create_menu_action was called once
            mock_create.assert_called_once()
            # Verify addAction was called once on the menu
            assert mock_menu.addAction.call_count == 1

    def test_add_playlist_deletion_actions(self, parent_widget, playlist_manager):
        """Test adding playlist deletion actions to the menu."""
        with patch.object(PlaylistContextMenuManager, "setup_menu"):
            manager = PlaylistContextMenuManager(parent_widget, playlist_manager)

        # Mock the _add_actions_from_list method
        with patch.object(manager, "_add_actions_from_list") as mock_add:
            mock_menu = MagicMock()
            manager._add_playlist_deletion_actions(mock_menu)

            # Verify _add_actions_from_list was called with 2 deletion actions
            mock_add.assert_called_once()
            actions_list = mock_add.call_args[0][1]
            assert len(actions_list) == 2  # Delete selected, Delete all


class TestFavouritesContextMenuManager:

    def test_init(self, parent_widget, favourites_manager):
        """Test initialization of FavouritesContextMenuManager."""
        with patch.object(FavouritesContextMenuManager, "setup_menu"):
            manager = FavouritesContextMenuManager(parent_widget, favourites_manager)

            assert isinstance(manager.favourites_commands, FavouritesManagerCommands)
            # Just verify the instance types without checking non-existent attributes
            assert isinstance(
                manager.favourites_commands.delete_selected,
                cmd.DeleteSelectedFavouriteCommand,
            )

    def test_setup_menu(self, parent_widget, favourites_manager):
        """Test setup_menu configures the context menu with all required actions."""
        # Mock the _add_actions_from_list method to avoid dealing with actual UI setup
        with patch.object(
            FavouritesContextMenuManager, "_add_actions_from_list"
        ) as mock_add:
            manager = FavouritesContextMenuManager(parent_widget, favourites_manager)

            # Verify context menu policy is set correctly
            assert (
                parent_widget.favourites_listWidget.contextMenuPolicy()
                == Qt.ActionsContextMenu
            )

            # Verify _add_actions_from_list was called with 2 actions
            mock_add.assert_called_once()
            actions_list = mock_add.call_args[0][1]
            assert len(actions_list) == 2  # Delete selected, Delete all


class TestContextMenuManager:

    def test_init(
        self, parent_widget, event_handler, favourites_manager, playlist_manager
    ):
        """Test initialization of ContextMenuManager."""
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
        """Test setup_all_menus creates all sub-managers correctly."""
        # Use the correct path for the imports in the patch
        # Instead of patching imports, create mock instances directly
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

            # Verify all managers were created with correct dependencies
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
        """Test PlaybackCommands dataclass structure."""
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
        """Test FavoriteCommands dataclass structure."""
        commands = FavoriteCommands(
            selected_to_favorites=cmd.SelectedToFavouritesCommand(favourites_manager),
            all_to_favorites=cmd.AllToFavouritesCommand(favourites_manager),
        )

        assert isinstance(
            commands.selected_to_favorites, cmd.SelectedToFavouritesCommand
        )
        assert isinstance(commands.all_to_favorites, cmd.AllToFavouritesCommand)

        # Don't check for non-existent attributes

    def test_playlist_commands(self, playlist_manager, parent_widget):
        """Test PlaylistCommands dataclass structure."""
        commands = PlaylistCommands(
            selected_to_playlist=cmd.SelectedToPlaylistCommand(
                playlist_manager, parent_widget
            ),
            all_to_playlist=cmd.AllToPlaylistCommand(playlist_manager, parent_widget),
        )

        assert isinstance(commands.selected_to_playlist, cmd.SelectedToPlaylistCommand)
        assert isinstance(commands.all_to_playlist, cmd.AllToPlaylistCommand)

        # Don't check for non-existent attributes

    def test_playlist_manager_commands(self, playlist_manager, parent_widget):
        """Test PlaylistManagerCommands dataclass structure."""
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

        # Don't check for non-existent attributes

    def test_favourites_manager_commands(self, favourites_manager):
        """Test FavouritesManagerCommands dataclass structure."""
        commands = FavouritesManagerCommands(
            delete_selected=cmd.DeleteSelectedFavouriteCommand(favourites_manager),
            delete_all=cmd.DeleteAllFavouriteCommand(favourites_manager),
        )

        assert isinstance(commands.delete_selected, cmd.DeleteSelectedFavouriteCommand)
        assert isinstance(commands.delete_all, cmd.DeleteAllFavouriteCommand)

        # Don't check for non-existent attributes like 'favourites_manager'

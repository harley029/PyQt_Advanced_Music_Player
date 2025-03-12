from unittest.mock import MagicMock

from interfaces.context.commands import (
    PlayCommand,
    PauseCommand,
    NextCommand,
    PreviousCommand,
    StopCommand,
    SelectedToFavouritesCommand,
    AllToFavouritesCommand,
    SelectedToPlaylistCommand,
    AllToPlaylistCommand,
    DeleteSelectedFavouriteCommand,
    DeleteAllFavouriteCommand,
    LoadPlaylistCommand,
    NewPlaylistCommand,
    DeletePlaylistCommand,
    DeleteAllPlaylistCommand,
)


def test_play_command_execute():
    """
    Test that PlayCommand.execute() calls the on_play_clicked method of the event handler.

    This test verifies that when the execute method of a PlayCommand instance is called,
    it correctly delegates to the on_play_clicked method of the event handler that was
    passed during initialization.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the on_play_clicked method of the event handler is not called exactly once.
    """
    event_handler = MagicMock()
    command = PlayCommand(event_handler)
    command.execute()
    event_handler.on_play_clicked.assert_called_once()


def test_pause_command_execute():
    """
    Test that PauseCommand.execute() calls the on_pause_clicked method of the event handler.

    This test verifies that when the execute method of a PauseCommand instance is called,
    it correctly delegates to the on_pause_clicked method of the event handler that was
    passed during initialization.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the on_pause_clicked method of the event handler is not called exactly once.
    """
    event_handler = MagicMock()
    command = PauseCommand(event_handler)
    command.execute()
    event_handler.on_pause_clicked.assert_called_once()


def test_next_command_execute():
    """
    Test that NextCommand.execute() calls the on_next_previous_clicked method with "forward" direction.

    This test verifies that when the execute method of a NextCommand instance is called,
    it correctly delegates to the on_next_previous_clicked method of the event handler with
    the "forward" direction parameter.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the on_next_previous_clicked method of the event handler is not called
                       exactly once with the direction="forward" parameter.
    """
    event_handler = MagicMock()
    command = NextCommand(event_handler)
    command.execute()
    event_handler.on_next_previous_clicked.assert_called_once_with(direction="forward")


def test_previous_command_execute():
    """
    Test that PreviousCommand.execute() calls the on_next_previous_clicked method with "backward" direction.

    This test verifies that when the execute method of a PreviousCommand instance is called,
    it correctly delegates to the on_next_previous_clicked method of the event handler with
    the "backward" direction parameter.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the on_next_previous_clicked method of the event handler is not called
                       exactly once with the direction="backward" parameter.
    """
    event_handler = MagicMock()
    command = PreviousCommand(event_handler)
    command.execute()
    event_handler.on_next_previous_clicked.assert_called_once_with(direction="backward")


def test_stop_command_execute():
    """
    Test that StopCommand.execute() calls the on_stop_clicked method of the event handler.

    This test verifies that when the execute method of a StopCommand instance is called,
    it correctly delegates to the on_stop_clicked method of the event handler that was
    passed during initialization.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the on_stop_clicked method of the event handler is not called exactly once.
    """
    event_handler = MagicMock()
    command = StopCommand(event_handler)
    command.execute()
    event_handler.on_stop_clicked.assert_called_once()


def test_selected_to_favourites_command_execute():
    """
    Test that SelectedToFavouritesCommand.execute() calls the add_to_favourites method.

    This test verifies that when the execute method of a SelectedToFavouritesCommand instance is called,
    it correctly delegates to the add_to_favourites method of the favourites manager that was
    passed during initialization.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the add_to_favourites method of the favourites manager is not called exactly once.
    """
    favourites_manager = MagicMock()
    favourites_manager.add_to_favourites = MagicMock()
    command = SelectedToFavouritesCommand(favourites_manager)
    command.execute()
    favourites_manager.add_to_favourites.assert_called_once()


def test_all_to_favourites_command_execute():
    """
    Test that AllToFavouritesCommand.execute() calls the add_all_to_favourites method.

    This test verifies that when the execute method of an AllToFavouritesCommand instance is called,
    it correctly delegates to the add_all_to_favourites method of the favourites manager that was
    passed during initialization.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the add_all_to_favourites method of the favourites manager is not called exactly once.
    """
    favourites_manager = MagicMock()
    favourites_manager.add_all_to_favourites = MagicMock()
    command = AllToFavouritesCommand(favourites_manager)
    command.execute()
    favourites_manager.add_all_to_favourites.assert_called_once()


def test_selected_to_playlist_command_execute():
    """
    Test that SelectedToPlaylistCommand.execute() calls the add_song_to_playlist method with parent.

    This test verifies that when the execute method of a SelectedToPlaylistCommand instance is called,
    it correctly delegates to the add_song_to_playlist method of the playlist manager with the parent
    parameter that was passed during initialization.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the add_song_to_playlist method of the playlist manager is not called
                       exactly once with the parent parameter.
    """
    playlist_manager = MagicMock()
    parent = MagicMock()
    playlist_manager.add_song_to_playlist = MagicMock()
    command = SelectedToPlaylistCommand(playlist_manager, parent)
    command.execute()
    playlist_manager.add_song_to_playlist.assert_called_once_with(parent)


def test_all_to_playlist_command_execute():
    """
    Test that AllToPlaylistCommand.execute() calls the add_all_to_playlist method with parent.

    This test verifies that when the execute method of an AllToPlaylistCommand instance is called,
    it correctly delegates to the add_all_to_playlist method of the playlist manager with the parent
    parameter that was passed during initialization.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the add_all_to_playlist method of the playlist manager is not called
                       exactly once with the parent parameter.
    """
    playlist_manager = MagicMock()
    parent = MagicMock()
    playlist_manager.add_all_to_playlist = MagicMock()
    command = AllToPlaylistCommand(playlist_manager, parent)
    command.execute()
    playlist_manager.add_all_to_playlist.assert_called_once_with(parent)


def test_delete_selected_favourite_command_execute():
    """
    Test that DeleteSelectedFavouriteCommand.execute() calls the remove_selected_favourite method.

    This test verifies that when the execute method of a DeleteSelectedFavouriteCommand instance is called,
    it correctly delegates to the remove_selected_favourite method of the favourites manager that was
    passed during initialization.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the remove_selected_favourite method of the favourites manager is not called exactly once.
    """
    favourites_manager = MagicMock()
    favourites_manager.remove_selected_favourite = MagicMock()
    command = DeleteSelectedFavouriteCommand(favourites_manager)
    command.execute()
    favourites_manager.remove_selected_favourite.assert_called_once()


def test_delete_all_favourite_command_execute():
    """
    Test that DeleteAllFavouriteCommand.execute() calls the clear_favourites method.

    This test verifies that when the execute method of a DeleteAllFavouriteCommand instance is called,
    it correctly delegates to the clear_favourites method of the favourites manager that was
    passed during initialization.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the clear_favourites method of the favourites manager is not called exactly once.
    """
    favourites_manager = MagicMock()
    favourites_manager.clear_favourites = MagicMock()
    command = DeleteAllFavouriteCommand(favourites_manager)
    command.execute()
    favourites_manager.clear_favourites.assert_called_once()


def test_load_playlist_command_execute():
    """
    Test that LoadPlaylistCommand.execute() calls the load_playlist_into_widget method with parent.

    This test verifies that when the execute method of a LoadPlaylistCommand instance is called,
    it correctly delegates to the load_playlist_into_widget method of the playlist manager with the parent
    parameter that was passed during initialization.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the load_playlist_into_widget method of the playlist manager is not called
                       exactly once with the parent parameter.
    """
    playlist_manager = MagicMock()
    parent = MagicMock()
    playlist_manager.load_playlist_into_widget = MagicMock()
    command = LoadPlaylistCommand(playlist_manager, parent)
    command.execute()
    playlist_manager.load_playlist_into_widget.assert_called_once_with(parent)


def test_new_playlist_command_execute():
    """
    Test that NewPlaylistCommand.execute() calls the create_playlist method with parent.

    This test verifies that when the execute method of a NewPlaylistCommand instance is called,
    it correctly delegates to the create_playlist method of the playlist manager with the parent
    parameter that was passed during initialization.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the create_playlist method of the playlist manager is not called
                       exactly once with the parent parameter.
    """
    playlist_manager = MagicMock()
    parent = MagicMock()
    playlist_manager.create_playlist = MagicMock()
    command = NewPlaylistCommand(playlist_manager, parent)
    command.execute()
    playlist_manager.create_playlist.assert_called_once_with(parent)


def test_delete_playlist_command_execute():
    """
    Test that DeletePlaylistCommand.execute() calls the remove_playlist method with parent.

    This test verifies that when the execute method of a DeletePlaylistCommand instance is called,
    it correctly delegates to the remove_playlist method of the playlist manager with the parent
    parameter that was passed during initialization.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the remove_playlist method of the playlist manager is not called
                       exactly once with the parent parameter.
    """
    playlist_manager = MagicMock()
    parent = MagicMock()
    playlist_manager.remove_playlist = MagicMock()
    command = DeletePlaylistCommand(playlist_manager, parent)
    command.execute()
    playlist_manager.remove_playlist.assert_called_once_with(parent)


def test_delete_all_playlist_command_execute():
    """
    Test that DeleteAllPlaylistCommand.execute() calls the remove_all_playlists method with parent.

    This test verifies that when the execute method of a DeleteAllPlaylistCommand instance is called,
    it correctly delegates to the remove_all_playlists method of the playlist manager with the parent
    parameter that was passed during initialization.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the remove_all_playlists method of the playlist manager is not called
                       exactly once with the parent parameter.
    """
    playlist_manager = MagicMock()
    parent = MagicMock()
    playlist_manager.remove_all_playlists = MagicMock()
    command = DeleteAllPlaylistCommand(playlist_manager, parent)
    command.execute()
    playlist_manager.remove_all_playlists.assert_called_once_with(parent)

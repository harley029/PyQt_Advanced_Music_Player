from unittest.mock import MagicMock

# Импортируем классы команд; замените 'commands' на правильный путь, если требуется.
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


# Тест для команды воспроизведения
def test_play_command_execute():
    event_handler = MagicMock()
    command = PlayCommand(event_handler)
    command.execute()
    event_handler.on_play_clicked.assert_called_once()


# Тест для команды паузы
def test_pause_command_execute():
    event_handler = MagicMock()
    command = PauseCommand(event_handler)
    command.execute()
    event_handler.on_pause_clicked.assert_called_once()


# Тест для команды "следующий трек"
def test_next_command_execute():
    event_handler = MagicMock()
    command = NextCommand(event_handler)
    command.execute()
    event_handler.on_next_previous_clicked.assert_called_once_with(direction="forward")


# Тест для команды "предыдущий трек"
def test_previous_command_execute():
    event_handler = MagicMock()
    command = PreviousCommand(event_handler)
    command.execute()
    event_handler.on_next_previous_clicked.assert_called_once_with(direction="backward")


# Тест для команды остановки воспроизведения
def test_stop_command_execute():
    event_handler = MagicMock()
    command = StopCommand(event_handler)
    command.execute()
    event_handler.on_stop_clicked.assert_called_once()


# Тест для команды добавления выбранных песен в избранное
def test_selected_to_favourites_command_execute():
    favourites_manager = MagicMock()
    favourites_manager.add_to_favourites = MagicMock()
    command = SelectedToFavouritesCommand(favourites_manager)
    command.execute()
    favourites_manager.add_to_favourites.assert_called_once()


# Тест для команды добавления всех песен в избранное
def test_all_to_favourites_command_execute():
    favourites_manager = MagicMock()
    favourites_manager.add_all_to_favourites = MagicMock()
    command = AllToFavouritesCommand(favourites_manager)
    command.execute()
    favourites_manager.add_all_to_favourites.assert_called_once()


# Тест для команды добавления выбранной песни в плейлист
def test_selected_to_playlist_command_execute():
    playlist_manager = MagicMock()
    parent = MagicMock()
    playlist_manager.add_song_to_playlist = MagicMock()
    command = SelectedToPlaylistCommand(playlist_manager, parent)
    command.execute()
    playlist_manager.add_song_to_playlist.assert_called_once_with(parent)


# Тест для команды добавления всех песен в плейлист
def test_all_to_playlist_command_execute():
    playlist_manager = MagicMock()
    parent = MagicMock()
    playlist_manager.add_all_to_playlist = MagicMock()
    command = AllToPlaylistCommand(playlist_manager, parent)
    command.execute()
    playlist_manager.add_all_to_playlist.assert_called_once_with(parent)


# Тест для команды удаления выбранного элемента из избранного
def test_delete_selected_favourite_command_execute():
    favourites_manager = MagicMock()
    favourites_manager.remove_selected_favourite = MagicMock()
    command = DeleteSelectedFavouriteCommand(favourites_manager)
    command.execute()
    favourites_manager.remove_selected_favourite.assert_called_once()


# Тест для команды удаления всех избранных
def test_delete_all_favourite_command_execute():
    favourites_manager = MagicMock()
    favourites_manager.clear_favourites = MagicMock()
    command = DeleteAllFavouriteCommand(favourites_manager)
    command.execute()
    favourites_manager.clear_favourites.assert_called_once()


# Тест для команды загрузки плейлиста
def test_load_playlist_command_execute():
    playlist_manager = MagicMock()
    parent = MagicMock()
    playlist_manager.load_playlist_into_widget = MagicMock()
    command = LoadPlaylistCommand(playlist_manager, parent)
    command.execute()
    playlist_manager.load_playlist_into_widget.assert_called_once_with(parent)


# Тест для команды создания нового плейлиста
def test_new_playlist_command_execute():
    playlist_manager = MagicMock()
    parent = MagicMock()
    playlist_manager.create_playlist = MagicMock()
    command = NewPlaylistCommand(playlist_manager, parent)
    command.execute()
    playlist_manager.create_playlist.assert_called_once_with(parent)


# Тест для команды удаления плейлиста
def test_delete_playlist_command_execute():
    playlist_manager = MagicMock()
    parent = MagicMock()
    playlist_manager.remove_playlist = MagicMock()
    command = DeletePlaylistCommand(playlist_manager, parent)
    command.execute()
    playlist_manager.remove_playlist.assert_called_once_with(parent)


# Тест для команды удаления всех плейлистов
def test_delete_all_playlist_command_execute():
    playlist_manager = MagicMock()
    parent = MagicMock()
    playlist_manager.remove_all_playlists = MagicMock()
    command = DeleteAllPlaylistCommand(playlist_manager, parent)
    command.execute()
    playlist_manager.remove_all_playlists.assert_called_once_with(parent)

from PyQt5.QtWidgets import QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from interfaces.context import commands as cmd
from interfaces.context.command_action import CommandAction
from utils import messages as msg


class ContextMenuManager:

    def __init__(self, parent, event_handler, favourites_manager, playlist_manager):
        self.parent = parent
        self.event_handler = event_handler
        self.favourites_manager = favourites_manager
        self.playlist_manager = playlist_manager
        self.create_commands()
        self.setup_menus()

    def create_commands(self):
        # Контекстное меню вкладки Favourites
        self.del_selected_fav_command = cmd.DeleteSelectedFavouriteCommand(self.favourites_manager)
        self.del_all_favourites_command = cmd.DeleteAllFavouriteCommand(self.favourites_manager)

        # Контекстное меню вкладки Playlist
        self.load_playlist_command = cmd.LoadPlaylistCommand(self.playlist_manager, self.parent)
        self.create_new_playlist_command = cmd.NewPlaylistCommand(self.playlist_manager, self.parent)
        self.del_sel_pl_command = cmd.DeletePlaylistCommand(self.playlist_manager, self.parent)
        self.del_all_pl_command = cmd.DeleteAllPlaylistCommand(self.playlist_manager, self.parent)

        # Контекстное меню вкладки Song List
        self.play_command = cmd.PlayCommand(self.event_handler)
        self.pause_command = cmd.PauseCommand(self.event_handler)
        self.next_command = cmd.NextCommand(self.event_handler)
        self.previous_command = cmd.PreviousCommand(self.event_handler)
        self.stop_command = cmd.StopCommand(self.event_handler)
        self.sel_to_fav_command = cmd.SelectedToFavouritesCommand(self.favourites_manager)
        self.all_to_fav_command = cmd.AllToFavouritesCommand(self.favourites_manager)
        self.sel_to_pl_command = cmd.SelectedToPlaylistCommand(self.playlist_manager, self.parent)
        self.all_to_pl_command = cmd.AllToPlaylistCommand(self.playlist_manager, self.parent)

    def setup_menus(self):
        self.setup_favourite_menu()
        self.setup_playlist_menu()
        self.setup_song_menu()

    # Настройка контекстного меню для Избранного
    def setup_favourite_menu(self):
        menu = self.parent.favourites_listWidget
        menu.setContextMenuPolicy(Qt.ActionsContextMenu)

        actionRemove_Selected_Favourite=CommandAction(QIcon(":/img/utils/images/clear.png"), msg.CTX_DEL_SEL, self.parent, self.del_selected_fav_command)
        ctionRemove_All_Favourites=CommandAction(QIcon(":/img/utils/images/remove.png"), msg.CTX_DEL_ALL, self.parent, self.del_all_favourites_command)

        menu.addAction(actionRemove_Selected_Favourite)
        separator = QAction(self.parent)
        separator.setSeparator(True)
        menu.addAction(separator)

        menu.addAction(ctionRemove_All_Favourites)

    # Настройка контекстного меню для Плейлистов
    def setup_playlist_menu(self):
        menu = self.parent.playlists_listWidget
        menu.setContextMenuPolicy(Qt.ActionsContextMenu)

        actionLoad_Selected_Playlist=CommandAction(QIcon(":/img/utils/images/music_list.png"), msg.CTX_LOAD_LST, self.parent, self.load_playlist_command)
        menu.addAction(actionLoad_Selected_Playlist)
        separator = QAction(self.parent)
        separator.setSeparator(True)
        menu.addAction(separator)

        actionCreate_New_Playlist=CommandAction(QIcon(":/img/utils/images/music_list.png"), msg.CTX_NEW_LST, self.parent, self.create_new_playlist_command)
        menu.addAction(actionCreate_New_Playlist)
        separator1 = QAction(self.parent)
        separator1.setSeparator(True)
        menu.addAction(separator1)

        actionDelete_Selected_Playlist=CommandAction(QIcon(":/img/utils/images/clear.png"), msg.CTX_DEL_SEL_LST, self.parent, self.del_sel_pl_command)
        actionDelete_All_Playlists=CommandAction(QIcon(":/img/utils/images/remove.png"), msg.CTX_DEL_ALL_LST, self.parent, self.del_all_pl_command)
        menu.addAction(actionDelete_Selected_Playlist)
        menu.addAction(actionDelete_All_Playlists)

       

    # Настройка контекстного меню для списка загруженных песен
    def setup_song_menu(self):
        menu = self.parent.loaded_songs_listWidget
        menu.setContextMenuPolicy(Qt.ActionsContextMenu)

        actionPlay = CommandAction(QIcon(":/img/utils/images/pase.png"), msg.CTX_PLAY, self.parent, self.play_command)
        actionPause_Unpause = CommandAction(QIcon(":/img/utils/images/play.png"), msg.CTX_PAUSE, self.parent, self.pause_command)
        actionNext = CommandAction(QIcon(":/img/utils/images/next.png"), msg.CTX_NEXT, self.parent, self.next_command)
        actionPrevious = CommandAction(QIcon(":/img/utils/images/pre.png"), msg.CTX_PREVS, self.parent, self.previous_command)
        actionStop = CommandAction(QIcon(":/img/utils/images/stop.png"), msg.CTX_STOP, self.parent, self.stop_command)
        menu.addAction(actionPlay)
        menu.addAction(actionPause_Unpause)
        menu.addAction(actionNext)
        menu.addAction(actionPrevious)
        menu.addAction(actionStop)
        separator1 = QAction(self.parent)
        separator1.setSeparator(True)
        menu.addAction(separator1)

        actionAdd_Selected_to_Favourites=CommandAction(QIcon(":/img/utils/images/like.png"), msg.CTX_ADD_TO_FAV, self.parent, self.sel_to_fav_command)
        actionAdd_all_to_Favourites=CommandAction(QIcon(":/img/utils/images/like.png"), msg.CTX_ADD_ALL_TO_FAV, self.parent, self.all_to_fav_command)
        menu.addAction(actionAdd_Selected_to_Favourites)
        menu.addAction(actionAdd_all_to_Favourites)
        separator2 = QAction(self.parent)
        separator2.setSeparator(True)
        menu.addAction(separator2)

        actionSave_Selected_to_a_Playlist=CommandAction(QIcon(":/img/utils/images/MusicListItem.png"), msg.CTX_ADD_TO_LST, self.parent, self.sel_to_pl_command)
        actionSave_all_to_a_Playlist=CommandAction(QIcon(":/img/utils/images/MusicListItem.png"), msg.CTX_ADD_ALL_TO_LST, self.parent, self.all_to_pl_command)
        menu.addAction(actionSave_Selected_to_a_Playlist)
        menu.addAction(actionSave_all_to_a_Playlist)

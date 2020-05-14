from .menu import LoadingMenu


class Loading:

    def enter_loading(self, rprops, track_name_transl, ranking, players):
        self.menu = LoadingMenu(
            rprops, self, track_name_transl, ranking, players)

    def exit_loading(self):
        self.menu.destroy()

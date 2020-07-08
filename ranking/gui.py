from logging import info
from panda3d.core import TextureStage
from direct.gui.OnscreenImage import OnscreenImage
from yyagl.lib.gui import Btn, Text, Img
from yyagl.lib.p3d.shader import load_shader
from yyagl.gameobject import GuiColleague
from yyagl.engine.gui.page import Page, PageGui, PageEvent
from yyagl.gameobject import GameObject
from yyagl.engine.gui.menu import Menu
from yracing.player.player import Player


class RankingPageGui(PageGui):

    def __init__(self, mediator, menu_props, rprops, sprops, ranking, players):
        self.rprops = rprops
        self.sprops = sprops
        # self.drivers = sprops.drivers
        self.ranking = ranking
        self.menu_props = menu_props
        self.__players = players
        PageGui.__init__(self, mediator, menu_props)

    def build(self, back_btn=True):  # parameters differ from overridden
        self.eng.init_gfx()
        self.font = self.menu_props.font
        self.text_fg = self.menu_props.text_active_col
        self.text_bg = self.menu_props.text_normal_col
        self.text_err_col = self.menu_props.text_err_col
        # items = self.ranking.carname2points.items()
        items = [(player.car, player.points) for player in self.__players]
        sorted_ranking = reversed(sorted(items, key=lambda el: el[1]))
        txt = Text(_('Ranking'), scale=.1, pos=(0, .76), font=self.font,
                   fg=self.text_bg)
        self.add_widgets([txt])
        for i, car in enumerate(sorted_ranking):
            txt, img = RankingGui.set_drv_txt_img(
                self, i, car[0], 0, .52, str(car[1]) + ' %s', self.__players)
            self.add_widgets([txt, img])
        track = self.rprops.track_name
        ntracks = len(self.sprops.gameprops.season_tracks)
        if self.sprops.gameprops.season_tracks.index(track) == ntracks - 1:
            cont_btn_cmd = self.notify
            cont_btn_ea = ['on_ranking_next_race']
            img = Img(
                'assets/images/gui/trophy.txo', parent=base.a2dRightCenter,
                pos=(-.58, 0), scale=.55)
            img.set_transparent()
            txt = Text(
                _('Congratulations!'), fg=(.8, .6, .2, 1), scale=.16,
                pos=(0, -.3), font=loader.loadFont(self.sprops.font),
                parent='leftcenter')
            txt.set_r(-79)
            self.add_widgets([txt, img])
        else:
            cont_btn_cmd = self.notify
            cont_btn_ea = ['on_ranking_end', self.__players]
        cont_btn = Btn(
            text=_('Continue'), pos=(0, -.8), cmd=cont_btn_cmd,
            extra_args=cont_btn_ea,
            **self.menu_props.btn_args)
        self.add_widgets([cont_btn])
        PageGui.build(self, False)


class RankingPage(Page):

    def __init__(self, rprops, sprops, menu_props, ranking, players):
        self.rprops = rprops
        self.menu_props = menu_props
        GameObject.__init__(self)
        self.event = PageEvent(self)
        self.gui = RankingPageGui(
            self, menu_props, rprops, sprops, ranking, players)
        # Page's __init__ is not invoked

    def attach_obs(self, mth):  # parameters differ from overridden
        self.gui.attach(mth)

    def detach_obs(self, mth):  # parameters differ from overridden
        self.gui.detach(mth)

    def destroy(self):
        self.event.destroy()
        self.gui.destroy()
        GameObject.destroy(self)


class RankingMenuGui(GuiColleague):

    def __init__(self, mediator, rprops, sprops, ranking, players):
        GuiColleague.__init__(self, mediator)
        menu_props = sprops.gameprops.menu_props
        menu_props.btn_size = (-8.6, 8.6, -.42, .98)
        #self.menu = RankingMenu(rprops, sprops, ranking, players)
        self.rank_page = RankingPage(
            rprops, sprops, menu_props, ranking, players)
        self.eng.do_later(.01, self.mediator.push_page, [self.rank_page])

    def destroy(self):
        self.rank_page.destroy()
        GuiColleague.destroy(self)


class RankingMenu(Menu):
    gui_cls = RankingMenuGui

    def __init__(self, rprops, sprops, ranking, players):
        self.__rprops = rprops
        self.__sprops = sprops
        self.__ranking = ranking
        self.__players = players
        menu_props = sprops.gameprops.menu_props
        Menu.__init__(self, menu_props)

    def _build_gui(self):
        self.gui = self.gui_cls(self, self.__rprops, self.__sprops,
                                self.__ranking, self.__players)

    def attach_obs(self, mth):
        self.gui.rank_page.attach_obs(mth)

    def detach_obs(self, mth):
        self.gui.rank_page.detach_obs(mth)

    def destroy(self):
        self.gui.destroy()
        GameObject.destroy(self)


class RankingGui(GuiColleague):

    def __init__(self, mediator, background_fpath, font, fg_col):
        GuiColleague.__init__(self, mediator)
        self.ranking_texts = []
        self.background_path = background_fpath
        self.font = font
        self.fg_col = fg_col
        self.rank_menu = self.background = None

    @staticmethod
    def set_drv_txt_img(page, i, car_name, pos_x, top, text, players):
        drivers = [player.driver for player in players]
        info('drivers: ' + str([drv for drv in drivers]))
        info('i: %s  - carname: %s - text: %s' % (
            i, car_name, text))
        drv = next(
            player.driver for player in players
            if player.car == car_name)
        player_car_names = [player.car for player in players
                            if player.kind == Player.human]
        is_player_car = car_name in player_car_names
        info('%s %s %s %s' % (
            text % drv.name, car_name, drv.img_idx, is_player_car))
        name = text % drv.name
        if '@' in name:
            name = name.split('@')[0] + '\1smaller\1@' + name.split('@')[1] + \
                '\2'
        txt = Text(
            name, align='left',
            scale=.072, pos=(pos_x, top - i * .16), font=page.font,
            fg=page.text_fg if is_player_car else page.text_bg)
        gprops = page.rprops.season_props.gameprops
        img = Img(
            gprops.cars_img % car_name,
            pos=(pos_x - .16, top + .02 - i * .16), scale=.074)
        filtervpath = RankingGui.eng.curr_path + \
            'yyagl/assets/shaders/filter.vert'
        with open(filtervpath) as fvs:
            vert = fvs.read()
        drvfpath = RankingGui.eng.curr_path + \
            'yyagl/assets/shaders/drv_car.frag'
        with open(drvfpath) as ffs:
            frag = ffs.read()
        shader = load_shader(vert, frag)
        if shader:
            img.set_shader(shader)
        img.set_transparent()
        t_s = TextureStage('ts')
        t_s.set_mode(TextureStage.MDecal)
        txt_path = gprops.drivers_img.path_sel % drv.img_idx
        img.set_texture(t_s, loader.loadTexture(txt_path))
        return txt, img

    def show(self, rprops, sprops, ranking, players):
        self.background = OnscreenImage(
            sprops.gameprops.menu_props.background_img_path,
            scale=(1.77778, 1, 1))
        self.background.setBin('background', 10)
        self.rank_menu = RankingMenu(rprops, sprops, ranking, players)

    def hide(self):
        self.background.destroy()
        self.rank_menu.destroy()

    def attach_obs(self, mth):
        self.rank_menu.attach_obs(mth)

    def detach_obs(self, mth):
        self.rank_menu.detach_obs(mth)

    def destroy(self):
        self.hide()
        self.rank_menu = self.ranking_texts = self.background = None
        GuiColleague.destroy(self)

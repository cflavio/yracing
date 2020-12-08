from panda3d.core import TextNode
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from yyagl.gameobject import GuiColleague
from yyagl.engine.gui.imgbtn import ImgBtn
from yracing.player.player import Player


class TuningGui(GuiColleague, DirectObject):

    def __init__(self, mediator, sprops):
        GuiColleague.__init__(self, mediator)
        self.buttons = self.background = None
        self.sprops = sprops
        self.txt = self.upg1_txt = self.upg2_txt = self.upg3_txt = \
            self.hint1_txt = self.hint2_txt = self.hint3_txt = None

    def show(self, players):
        self.background = OnscreenImage(
            self.sprops.gameprops.menu_props.background_img_path,
            scale=(1.77778, 1, 1))
        self.background.setBin('background', 10)
        bprops = {'scale': (.4, .4), 'cmd': self.on_btn}
        self.txt = OnscreenText(
            text=_('What do you want to upgrade?'), scale=.1, pos=(0, .76),
            font=loader.loadFont(self.sprops.font),
            fg=self.sprops.gameprops.menu_props.text_normal_col)
        self.buttons = [ImgBtn(
            pos=(-1.2, .1), img=self.sprops.tuning_imgs[0],
            extra_args=['engine'], **bprops)]
        self.buttons += [ImgBtn(
            pos=(0, .1), img=self.sprops.tuning_imgs[1],
            extra_args=['tires'], **bprops)]
        self.buttons += [ImgBtn(
            pos=(1.2, .1), img=self.sprops.tuning_imgs[2],
            extra_args=['suspensions'], **bprops)]
        self._set_events()
        # tuning = self.mediator.car2tuning[self.sprops.player_car_name]
        player_car_name = [player.car for player in players
                           if player.kind == Player.human][0]
        tuning = [player.tuning for player in players
                  if player.car == player_car_name][0]
        self.upg1_txt = OnscreenText(
            text=_('current upgrades: +') + str(tuning.engine),
            scale=.06,
            pos=(-1.53, -.36), font=loader.loadFont(self.sprops.font),
            wordwrap=12, align=TextNode.ALeft,
            fg=self.sprops.gameprops.menu_props.text_normal_col)
        self.upg2_txt = OnscreenText(
            text=_('current upgrades: +') + str(tuning.tires),
            scale=.06,
            pos=(-.35, -.36), font=loader.loadFont(self.sprops.font),
            wordwrap=12, align=TextNode.ALeft,
            fg=self.sprops.gameprops.menu_props.text_normal_col)
        self.upg3_txt = OnscreenText(
            text=_('current upgrades: +') + str(tuning.suspensions),
            scale=.06,
            pos=(.85, -.36), font=loader.loadFont(self.sprops.font),
            wordwrap=12, align=TextNode.ALeft,
            fg=self.sprops.gameprops.menu_props.text_normal_col)
        self.hint1_txt = OnscreenText(
            text=_("engine: it increases car's maximum speed"),
            scale=.06,
            pos=(-1.53, -.46), font=loader.loadFont(self.sprops.font),
            wordwrap=12, align=TextNode.ALeft,
            fg=self.sprops.gameprops.menu_props.text_normal_col)
        self.hint2_txt = OnscreenText(
            text=_("tires: they increase car's adherence"),
            scale=.06,
            pos=(-.35, -.46), font=loader.loadFont(self.sprops.font),
            wordwrap=12, align=TextNode.ALeft,
            fg=self.sprops.gameprops.menu_props.text_normal_col)
        self.hint3_txt = OnscreenText(
            text=_("suspensions: they increase car's stability"),
            scale=.06,
            pos=(.85, -.46), font=loader.loadFont(self.sprops.font),
            wordwrap=12, align=TextNode.ALeft,
            fg=self.sprops.gameprops.menu_props.text_normal_col)

    def _set_events(self):
        self._curr_btn = 0
        self.buttons[0]._on_enter(None)
        self.accept('joypad0-dpad_left-up', self.__on_evt, ['left'])
        self.accept('joypad0-dpad_right-up', self.__on_evt, ['right'])
        self.accept('joypad0-face_a-up', self.__on_evt, ['enter'])
        nav = self.sprops.gameprops.menu_props.nav.navinfo_lst[0]
        self.accept(self.eng.lib.remap_str(nav.left), self.__on_evt, ['left'])
        self.accept(self.eng.lib.remap_str(nav.right), self.__on_evt, ['right'])
        self.accept(self.eng.lib.remap_str(nav.fire), self.__on_evt, ['enter'])

    def __on_evt(self, evt):
        self.buttons[self._curr_btn]._on_exit(None)
        d = 1 if evt == 'right' else (-1 if evt == 'left' else 0)
        self._curr_btn = min(2, max(0, self._curr_btn + d))
        self.buttons[self._curr_btn]._on_enter(None)
        if evt == 'enter':
            self.on_btn(self.buttons[self._curr_btn].wdg['extraArgs'][0])

    def on_btn(self, val):
        self.notify('on_tuning_sel', val)

    def hide(self):
        wdgs = [self.background, self.txt, self.hint1_txt, self.hint2_txt,
                self.hint3_txt, self.upg1_txt, self.upg2_txt,
                self.upg3_txt]
        list(map(lambda wdg: wdg.destroy(), self.buttons + wdgs))
        self.ignore_all()

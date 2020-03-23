from abc import ABCMeta
from yyagl.gameobject import GameObject
from .logic import RaceLogic, RaceLogicSinglePlayer, RaceLogicServer, \
    RaceLogicClient
from .event import RaceEvent, RaceEventServer, RaceEventClient
from .gui.gui import RaceGui, RaceGuiServer
from .fsm import RaceFsm, RaceFsmServer, RaceFsmClient


class RaceFacade:

    @property
    def results(self): return self.gui.results

    def attach_obs(self, obs_meth, sort=10, rename='', args=[]):
        return self.event.attach(obs_meth, sort, rename, args)
    def detach_obs(self, obs_meth, lambda_call=None):
        return self.event.detach(obs_meth, lambda_call)


class Race(GameObject, RaceFacade):
    __metaclass__ = ABCMeta
    logic_cls = RaceLogic
    event_cls = RaceEvent
    fsm_cls = RaceFsm
    gui_cls = RaceGui

    def __init__(self, race_props, players):
        rpr = race_props
        GameObject.__init__(self)
        self.fsm = self.fsm_cls(self, rpr.shaders_dev, rpr.pbr)
        self.gui = self.gui_cls(self, rpr, players)
        self.logic = self.logic_cls(self, rpr)
        self.event = self.event_cls(self, rpr.ingame_menu, rpr.keys, players)

    def destroy(self):
        self.fsm.destroy()
        self.gui.destroy()
        self.logic.destroy()
        self.event.destroy()
        GameObject.destroy(self)


class RaceSinglePlayer(Race):
    logic_cls = RaceLogicSinglePlayer


class RaceServer(Race):
    logic_cls = RaceLogicClient
    event_cls = RaceEventServer
    fsm_cls = RaceFsmClient
    gui_cls = RaceGuiServer


class RaceClient(Race):
    logic_cls = RaceLogicClient
    event_cls = RaceEventClient
    fsm_cls = RaceFsmClient

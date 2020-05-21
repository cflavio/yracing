from logging import info
from yyagl.gameobject import GameObject, AiColleague
from .fsm import CarFsm, CarPlayerFsm
from .gfx import CarGfx, CarPlayerGfx, CarNetworkGfx
from .phys import CarPhys, CarPlayerPhys
from .event import CarEvent, CarPlayerEvent, CarPlayerEventServer, \
    CarPlayerEventClient, CarNetworkEvent, CarAiEvent, CarAiPlayerEvent
from .logic import CarLogic, CarPlayerLogic
from .audio import CarAudio, CarPlayerAudio
from .gui import CarGui, CarPlayerGui, CarPlayerLocalMPGui, \
    CarPlayerMPGui, CarNetworkGui
from .ai import CarAi


class CarProps:

    def __init__(
            self, race_props, name, pos, hpr, callback, race, driver_engine,
            driver_tires, driver_suspensions, track_waypoints,
            track_skidmark_col, ai_poller):
        self.race_props = race_props
        self.name = name
        self.pos = pos
        self.hpr = hpr
        self.callback = callback
        self.race = race
        self.driver_engine = driver_engine
        self.driver_tires = driver_tires
        self.driver_suspensions = driver_suspensions
        self.track_waypoints = track_waypoints
        self.track_skidmark_col = track_skidmark_col
        self.ai_poller = ai_poller


class CarFacade:

    @property
    def lap_times(self): return self.logic.lap_times

    @property
    def path(self): return self.gfx.path

    @property
    def laps_num(self): return self.logic.laps_num

    @property
    def name(self): return self.logic.cprops.name

    @property
    def laps(self): return self.logic.cprops.race_props.laps

    @property
    def pos(self): return self.gfx.nodepath.get_pos()

    @property
    def heading(self): return self.gfx.nodepath.h

    def attach_obs(self, obs_meth, sort=10, rename='', args=None):
        return self.event.attach(obs_meth, sort, rename, args or [])

    def detach_obs(self, obs_meth, lambda_call=None):
        return self.event.detach(obs_meth, lambda_call)

    def last_wp_not_fork(self): return self.logic.last_wp_not_fork()
    def not_fork_wps(self): return self.logic.not_fork_wps()
    def reparent(self): return self.gfx.reparent()
    def reset_car(self): return self.logic.reset_car()
    def start(self): return self.event.start()
    def get_pos(self): return self.gfx.nodepath.get_pos()
    def get_hpr(self): return self.gfx.nodepath.get_hpr()
    def closest_wp(self): return self.logic.closest_wp()
    def upd_ranking(self, ranking): return self.gui.upd_ranking(ranking)

    def get_linear_velocity(self):
        return self.phys.vehicle.get_chassis().get_linear_velocity()

    def demand(self, tgt_state, *args):
        return self.fsm.demand(tgt_state, *args)


class Car(GameObject, CarFacade):
    fsm_cls = CarFsm
    gfx_cls = CarGfx
    gui_cls = CarGui
    phys_cls = CarPhys
    event_cls = CarEvent
    logic_cls = CarLogic
    ai_cls = AiColleague
    audio_cls = CarAudio

    def __init__(self, car_props, player_car_idx, tuning, players):
        info('init car ' + car_props.name)
        self.player_car_idx = player_car_idx
        self._tuning = tuning
        self._car_props = car_props
        self._players = players
        GameObject.__init__(self)
        taskMgr.add(self._build_comps())

    async def _build_comps(self):
        self.fsm = self.fsm_cls(self, self._car_props, self._players)
        gfx_task = taskMgr.add(self._build_gfx)
        await gfx_task
        self.phys = self.phys_cls(self, self._car_props, self._tuning,
                                  self._players)
        self.gfx.set_emitters()
        self.logic = self.logic_cls(self, self._car_props, self._players)
        self.gui = self.gui_cls(self, self._car_props, self._players)
        self.event = self.event_cls(self, self._car_props.race_props,
                                    self._players)
        self.ai = self.ai_cls(self)
        self.audio = self.audio_cls(self, self._car_props.race_props)
        self._car_props.callback()

    def _build_gfx(self, task):
        self.gfx = self.gfx_cls(self, self._car_props)

    def destroy(self):
        self.fsm.destroy()
        self.gfx.destroy()
        self.phys.destroy()
        self.logic.destroy()
        self.gui.destroy()
        self.event.destroy()
        self.ai.destroy()
        self.audio.destroy()
        GameObject.destroy(self)


class CarPlayer(Car):
    event_cls = CarPlayerEvent
    audio_cls = CarPlayerAudio
    gui_cls = CarPlayerGui
    logic_cls = CarPlayerLogic
    phys_cls = CarPlayerPhys
    gfx_cls = CarPlayerGfx
    fsm_cls = CarPlayerFsm


class CarPlayerServer(Car):
    event_cls = CarPlayerEventServer
    audio_cls = CarPlayerAudio
    gui_cls = CarPlayerMPGui
    logic_cls = CarPlayerLogic


class CarPlayerClient(Car):
    event_cls = CarPlayerEventClient
    audio_cls = CarPlayerAudio
    gui_cls = CarPlayerMPGui
    logic_cls = CarPlayerLogic


class CarPlayerLocalMP(CarPlayer):
    gui_cls = CarPlayerLocalMPGui


class NetworkCar(Car):
    gfx_cls = CarNetworkGfx
    event_cls = CarNetworkEvent
    gui_cls = CarNetworkGui


class AiCar(Car):
    ai_cls = CarAi
    event_cls = CarAiEvent

    async def _build_comps(self):
        self.fsm = self.fsm_cls(self, self._car_props, self._players)
        gfx_task = taskMgr.add(self._build_gfx)
        await gfx_task
        self.phys = self.phys_cls(self, self._car_props, self._tuning,
                                  self._players)
        self.gfx.set_emitters()
        self.logic = self.logic_cls(self, self._car_props, self._players)
        self.gui = self.gui_cls(self)
        self.event = self.event_cls(self, self._car_props.race_props,
                                    self._players)
        self.ai = self.ai_cls(self, self._car_props, self._players)
        self.audio = self.audio_cls(self)
        self._car_props.callback()


class AiCarPlayer(AiCar, CarPlayer):
    event_cls = CarAiPlayerEvent

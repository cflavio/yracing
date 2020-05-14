from yyagl.gameobject import GameObject
from .logic import SeasonLogic


class SeasonProps:

    def __init__(
            self, gameprops, cars_number, tuning_imgs, font, countdown_sfx,
            single_race, wpn2img, race_start_time, countdown_seconds, camera,
            kind, room=None):
        self.gameprops = gameprops
        self.cars_number = cars_number
        self.tuning_imgs = tuning_imgs
        self.font = font
        self.countdown_sfx = countdown_sfx
        self.single_race = single_race
        self.wpn2img = wpn2img
        self.race_start_time = race_start_time
        self.countdown_seconds = countdown_seconds
        self.camera = camera
        self.kind = kind
        self.room = room


class SeasonFacade:

    @property
    def ranking(self): return self.logic.ranking

    @property
    def tuning(self): return self.logic.tuning

    @property
    def props(self): return self.logic.props

    @property
    def race(self): return self.logic.race

    def attach_obs(self, obs_meth, sort=10, rename='', args=None):
        return self.logic.attach(obs_meth, sort, rename, args or [])
    def detach_obs(self, obs_meth, lambda_call=None):
        return self.logic.detach(obs_meth, lambda_call)

    def start(self, reset=True): return self.logic.start(reset)
    def load(self, ranking, tuning, drivers):
        return self.logic.load(ranking, tuning, drivers)
    def create_race_server(self, race_props, players):
        return self.logic.create_race_server(race_props, players)
    def create_race_client(self, race_props, players):
        return self.logic.create_race_client(race_props, players)
    def create_race(self, race_props, players):
        return self.logic.create_race(race_props, players)

    @property
    def drivers_skills(self):
        return self.logic.props.gameprops.drivers_skills

    @drivers_skills.setter
    def drivers_skills(self, val):
        self.logic.drivers_skills = val


class Season(GameObject, SeasonFacade):
    logic_cls = SeasonLogic

    def __init__(self, season_props):
        GameObject.__init__(self)
        self.logic = self.logic_cls(self, season_props)

    def destroy(self):
        self.logic.destroy()
        GameObject.destroy(self)


class SingleRaceSeason(Season):
    pass

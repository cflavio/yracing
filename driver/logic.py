from yyagl.gameobject import LogicColleague, GameObject
from yracing.car.car import Car, CarProps, CarPlayer, CarPlayerServer, \
    CarPlayerClient, NetworkCar, AiCar, AiCarPlayer, CarPlayerLocalMP
from yracing.player.player import Player


class DriverLoaderStrategy(GameObject):

    @staticmethod
    def load(cars, r_p, car_name, track, race, player_car_name, player_car_names, s_p, aipoller, cb, players):
        if not cars: return cb()
        eng = DriverLoaderStrategy.eng
        car = cars.pop(0)
        car_cls = Car
        if eng.server.is_active or eng.client.is_active:
            car_cls = NetworkCar  # if car in player_cars else Car
        no_p = car not in player_car_names
        car_cls = AiCar if no_p and race.__class__.__name__ == 'RaceSinglePlayer' else car_cls
        race.logic.cars += [DriverLoaderStrategy.actual_load(
            cars, car, r_p, track, race, car_cls, player_car_name, player_car_names, s_p, aipoller, cb, 0, players)]

    @staticmethod
    def actual_load(cars, load_car_name, r_p, track, race, car_cls,
                    player_car_name, player_car_names, seas_p, aipoller, cb, player_car_idx, players):
        #drivers = [player.driver for player in players]
        #for _drv in drivers:
        #    if _drv.dprops.car_name == load_car_name:
        #        drv = _drv
        for _player in players:
            if _player.car == load_car_name:
                player = _player
        s_p = track.get_start_pos_hpr(r_p.grid.index(load_car_name))
        pos, hpr = s_p[0] + (0, 0, .2), s_p[1]
        player_car_name = [player.driver for player in players if player.kind == Player.human][0]
        if load_car_name == player_car_name:
            if r_p.start_wp:
                wp = [wp for wp in track.phys.waypoints if wp.get_name() == 'Waypoint%s' % r_p.start_wp][0]
                pos = wp.node.get_pos()
        car_props = CarProps(
            r_p, load_car_name, pos, hpr,
            lambda: DriverPlayerLoaderStrategy.load(cars, r_p, load_car_name, track,
                                                    race, player_car_name, player_car_names, seas_p, aipoller, cb, players),
            race, player.tuning.engine, player.tuning.tires,
            player.tuning.suspensions, race.track.phys.waypoints, race.track.phys.skidmark_col, aipoller)
        if player_car_idx == -1:
            return car_cls(car_props, player_car_idx, player.tuning, players)
        else:
            return car_cls(car_props, player_car_idx, player.tuning, players)


class DriverPlayerLoaderStrategy(GameObject):

    @staticmethod
    def load(loadcars, r_p, car_name, track, race, player_car_name, player_car_names, s_p, aipoller, cb, players):
        if not loadcars: return cb()
        eng = DriverLoaderStrategy.eng
        car = loadcars.pop(0)
        local_mp = s_p.kind == 'localmp'
        if local_mp and car in player_car_names or not local_mp and car == player_car_name or \
               s_p.kind == 'onlinemp' and car in player_car_names:
            if r_p.a_i == 1 or r_p.a_i == 2 and car != player_car_names[0]:
                car_cls = AiCarPlayer
            else:
                car_cls = CarPlayerLocalMP if car in player_car_names and player_car_names != [player_car_name] else CarPlayer
                if eng.client and eng.client.is_server_active:
                    car_cls = CarPlayerServer
                if eng.client and eng.client.is_client_active:
                    car_cls = CarPlayerClient
            idx = 0 if car_cls in [CarPlayerServer, CarPlayerClient] else player_car_names.index(car)
            race.logic.player_cars += [DriverLoaderStrategy.actual_load(
                loadcars, car, r_p, track, race, car_cls, player_car_name, player_car_names, s_p, aipoller, cb, idx, players)]
        else:
            car_cls = Car
            if eng.server.is_active or eng.client.is_active:
                car_cls = NetworkCar  # if car in player_cars else Car
            no_p = car not in player_car_names
            car_cls = AiCar if no_p and race.__class__.__name__ == 'RaceSinglePlayer' else car_cls
            race.logic.cars += [DriverLoaderStrategy.actual_load(
                loadcars, car, r_p, track, race, car_cls, player_car_name, player_car_names, s_p, aipoller, cb, -1, players)]


class DriverLogic(LogicColleague):

    def __init__(self, mediator, driver_props):
        LogicColleague.__init__(self, mediator)
        self.dprops = driver_props

    def to_dct(self):
        dct = {
            'img_idx': self.dprops.info.img_idx,
            'name': self.dprops.info.name,
            'speed': self.dprops.info.speed,
            'adherence': self.dprops.info.adherence,
            'stability': self.dprops.info.stability,
            'car_name': self.dprops.car_name,
            'f_engine': self.dprops.f_engine,
            'f_tires': self.dprops.f_tires,
            'f_suspensions': self.dprops.f_suspensions}
        return dct

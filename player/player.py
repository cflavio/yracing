from yracing.driver.driver import Driver


class TuningPlayer:

    def __init__(self, engine, tires, suspensions):
        self.engine = engine
        self.tires = tires
        self.suspensions = suspensions

    def __repr__(self):
        return 'tuning(%s %s %s)' % (
            self.engine, self.tires, self.suspensions)

    def to_json(self):
        return {
            'engine': self.engine, 'tires': self.tires,
            'suspensions': self.suspensions}

    @staticmethod
    def from_json(dct):
        return TuningPlayer(dct['engine'], dct['tires'], dct['suspensions'])


class Player:

    human, ai, network = range(3)

    def __init__(
            self, driver=None, car=None, kind=None, tuning=None,
            human_idx=None, name='', points=0):
        self.driver = driver
        self.car = car
        self.kind = kind
        self.tuning = tuning
        self.human_idx = human_idx
        self.name = name
        self.points = points

    def __repr__(self):
        return 'player(%s %s %s %s %s %s)' % (
            self.driver, self.car, self.kind, self.tuning, self.human_idx,
            self.name)

    def to_json(self):
        return {
            'driver': self.driver.to_json(), 'car': self.car, 'kind': self.kind,
            'tuning': self.tuning.to_json(), 'human_idx': self.human_idx,
            'name': self.name, 'points': self.points}

    @staticmethod
    def from_json(dct):
        return Player(
            Driver.from_json(dct['driver']), dct['car'], dct['kind'],
            TuningPlayer.from_json(dct['tuning']), dct['human_idx'], dct['name'],
            dct['points'])

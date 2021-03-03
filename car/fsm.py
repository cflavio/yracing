from yyagl.gameobject import FsmColleague
from yracing.car.ai import CarResultsAi


class CarFsm(FsmColleague):

    def __init__(self, mediator, car_props, players):
        FsmColleague.__init__(self, mediator)
        self.defaultTransitions = {'Loading': ['Countdown'],
                                   'Countdown': ['Play', 'Pause'],
                                   'Play': ['Waiting', 'Results', 'Pause'],
                                   'Pause': ['Play', 'Countdown'],
                                   'Waiting': ['Results']}
        self.cprops = car_props
        self.__players = players

    def enterPlay(self):
        self.mediator.audio.on_play()

    def enterWaiting(self):
        # state = self.getCurrentOrNextState()
        # self.mediator.event.input_bld = InputBuilder.create(state, has_j)
        self.mediator.ai.destroy()
        self.mediator.ai = CarResultsAi(
            self.mediator, self.cprops, self.__players)
        self.mediator.gui.hide()
        # self.mediator.gui.panel.enter_waiting()


class CarPlayerFsm(CarFsm):

    def enterWaiting(self):
        CarFsm.enterWaiting(self)
        self.mediator.gui.panel.enter_waiting()

    def enterResults(self):
        self.mediator.gui.panel.exit_waiting()

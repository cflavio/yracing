from abc import ABCMeta
from yyagl.gameobject import GameObject
# from .logic import RankingLogic
from .gui import RankingGui


class RankingFacade:

    # [('carname2points', lambda obj: obj.logic.carname2points)]
    # ('load', lambda obj: obj.logic.load),
    def show(self, rprops, sprops, ranking, players):
        return self.gui.show(rprops, sprops, ranking, players)

    def hide(self): return self.gui.hide()
    def reset(self): return self.logic.reset()
    def attach_obs(self, obs_meth, sort=10, rename='', args=None):
        return self.gui.attach_obs(obs_meth)
    def detach_obs(self, obs_meth, lambda_call=None):
        return self.gui.detach_obs(obs_meth)


class Ranking(GameObject, RankingFacade):
    __metaclass__ = ABCMeta

    def __init__(self, car_names, background_fpath, font, fg_col):
        # unused car_names
        GameObject.__init__(self)
        self.gui = RankingGui(self, background_fpath, font, fg_col)
        # self.logic = RankingLogic(self, car_names)

    def destroy(self):
        self.gui.destroy()
        # self.logic.destroy()
        GameObject.destroy(self)

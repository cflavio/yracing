from abc import ABCMeta
from yyagl.gameobject import GameObject
#from .logic import RankingLogic
from .gui import RankingGui


class RankingFacade:

    # [('carname2points', lambda obj: obj.logic.carname2points)]
    #('load', lambda obj: obj.logic.load),
    def show(self): return self.gui.show()
    def hide(self): return self.gui.hide()
    def reset(self): return self.logic.reset()
    def attach_obs(self, obs_meth, sort=10, rename='', args=[]):
        return self.gui.attach(obs_meth, sort, rename, args)
    def detach_obs(self, obs_meth, lambda_call=None):
        return self.gui.detach(obs_meth, lambda_call)


class Ranking(GameObject, RankingFacade):
    __metaclass__ = ABCMeta

    def __init__(self, car_names, background_fpath, font, fg_col):
        GameObject.__init__(self)
        self.gui = RankingGui(self, background_fpath, font, fg_col)
        #self.logic = RankingLogic(self, car_names)

    def destroy(self):
        self.gui.destroy()
        #self.logic.destroy()
        GameObject.destroy(self)

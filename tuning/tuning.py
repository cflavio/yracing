from abc import ABCMeta
from yyagl.gameobject import GameObject
from .gui import TuningGui


class TuningFacade:

    # [('car2tuning', lambda obj: obj.logic.car2tuning),
    #            ('to_dct', lambda obj: obj.logic.to_dct)]
    def attach_obs(self, obs_meth, sort=10, rename='', args=[]):
        return self.gui.attach(obs_meth, sort, rename, args)
    def detach_obs(self, obs_meth, lambda_call=None):
        return self.gui.detach(obs_meth, lambda_call)
    #('load', lambda obj: obj.logic.load),
    def show_gui(self): return self.gui.show()
    def hide_gui(self): return self.gui.hide()


class Tuning(GameObject, TuningFacade):
    __metaclass__ = ABCMeta

    def __init__(self, props):
        GameObject.__init__(self)
        self.gui = TuningGui(self, props)

    def destroy(self):
        self.gui.destroy()
        GameObject.destroy(self)

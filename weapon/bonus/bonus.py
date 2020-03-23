from yyagl.gameobject import GameObject
from .gfx import BonusGfx
from .phys import BonusPhys
from .event import BonusEvent
from .logic import BonusLogic


class BonusFacade:

    @property
    def pos(self): return self.phys.pos
    def attach_obs(self, obs_meth, sort=10, rename='', args=[]):
        return self.event.attach(obs_meth, sort, rename, args)
    def detach_obs(self, obs_meth, lambda_call=None):
        return self.event.detach(obs_meth, lambda_call)


class Bonus(GameObject, BonusFacade):

    def __init__(self, pos, model_name, model_suff, track_phys, track_gfx):
        GameObject.__init__(self)
        self.gfx = BonusGfx(self, pos, model_name, model_suff)
        self.event = BonusEvent(self)
        self.phys = BonusPhys(self, pos)
        self.logic = BonusLogic(self, track_phys, track_gfx)

    def destroy(self):
        self.gfx.destroy()
        self.event.destroy()
        self.phys.destroy()
        self.logic.destroy()
        GameObject.destroy(self)

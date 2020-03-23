from yyagl.gameobject import GameObject
from .gfx import WeaponGfx
from .audio import WeaponAudio


class WeaponFacade:

    @property
    def id(self): return self.logic.wpn_id
    def attach_obs(self, obs_meth, sort=10, rename='', args=[]):
        return self.logic.attach(obs_meth, sort, rename, args)
    def detach_obs(self, obs_meth, lambda_call=None):
        return self.logic.detach(obs_meth, lambda_call)
    def fire(self, sfx): return self.logic.fire(sfx)
    def update_props(self, pos, fwd): return self.logic.update_props(pos, fwd)
    def update_fired_props(self, pos, fwd): return self.logic.update_fired_props(pos, fwd)
    def ai_fire(self): return self.ai.update()
    def reparent(self, parent): return self.gfx.reparent(parent)


class Weapon(GameObject, WeaponFacade):

    gfx_cls = WeaponGfx
    audio_cls = WeaponAudio
    deg = 0

    def __init__(self, car, path, cars, part_path, wpn_id, players):
        GameObject.__init__(self)
        self.gfx = self.gfx_cls(self, car.gfx.nodepath, path)
        self.audio = self.audio_cls(self)
        self.logic = self.logic_cls(self, car, cars, wpn_id)
        self.ai = self.ai_cls(self, car)

    def destroy(self):
        self.gfx.destroy()
        self.audio.destroy()
        self.logic.destroy()
        self.ai.destroy()
        GameObject.destroy(self)


class PhysWeapon(Weapon):

    def __init__(self, car, path, cars, part_path, wpn_id, players):
        GameObject.__init__(self)
        self.gfx = self.gfx_cls(self, car.gfx.nodepath, path)
        self.phys = self.phys_cls(self, car, cars, players)
        self.audio = self.audio_cls(self)
        self.logic = self.logic_cls(self, car, cars, wpn_id)
        self.event = self.event_cls(self, part_path)
        self.ai = self.ai_cls(self, car)
        WeaponFacade.__init__(self)
        # refactor: call Weapon.__init__

    def destroy(self):
        self.phys.destroy()
        self.event.destroy()
        Weapon.destroy(self)

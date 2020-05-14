from logging import info
from yyagl.gameobject import GameObject
from .gfx import TrackGfx, TrackGfxShader, TrackGfxDebug, TrackGfxPbr
from .phys import TrackPhys
from .audio import TrackAudio


class TrackFacade:

    @property
    def bounds(self): return self.phys.bounds

    def get_start_pos_hpr(self, idx): return self.phys.get_start_pos_hpr(idx)
    def play_music(self): return self.audio.music.play()
    def stop_music(self): return self.audio.music.stop()
    def update(self): return self.event.update()
    def reparent_to(self, node): return self.gfx.model.reparent_to(node)

    def attach_obs(self, obs_meth, sort=10, rename='', args=None):
        return self.attach(obs_meth, sort, rename, args or [])
    def detach_obs(self, obs_meth, lambda_call=None):
        return self.detach(obs_meth, lambda_call)


class Track(GameObject, TrackFacade):

    def __init__(self, race_props):
        info('init track')
        self.gfx = None
        self.race_props = self.__rpr = race_props
        self.__gfx_cls = TrackGfx
        if self.__rpr.shaders_dev: self.__gfx_cls = TrackGfxShader
        if self.__rpr.pbr: self.__gfx_cls = TrackGfxPbr
        self.__gfx_cls = TrackGfxDebug if self.__rpr.show_waypoints \
            else self.__gfx_cls
        GameObject.__init__(self)
        taskMgr.add(self.__build_comps())

    async def __build_comps(self):
        gfx_task = taskMgr.add(self.__build_gfx)
        await gfx_task
        self.phys = TrackPhys(self, self.__rpr)
        self.audio = TrackAudio(self, self.__rpr.music_path)
        self.notify('on_track_loaded')

    def __build_gfx(self, task):  # unused task
        self.gfx = self.__gfx_cls(self, self.__rpr)

    def destroy(self):
        self.gfx.destroy()
        self.phys.destroy()
        self.audio.destroy()
        GameObject.destroy(self)

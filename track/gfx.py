from logging import info
from os.path import exists
from os import system
from sys import executable
from panda3d.core import NodePath, LPoint3f, LineSegs, BitMask32
from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gfx import AnimNode, AmbientLight, Spotlight
from yyagl.gameobject import GfxColleague
from yyagl.lib.p3d.gfx import P3dNode
from yracing.bitmasks import BitMasks
from .signs import Signs


class TrackGfx(GfxColleague):

    def __init__(self, mediator, race_props):
        self.ambient_np = self.spot_lgt = self.model = self.empty_models = \
            self.signs = self.ambient = None
        self.__anim_nodes = []
        self.__flat_roots = {}
        self.raceprops = race_props
        GfxColleague.__init__(self, mediator)
        # taskMgr.add(self.__set_meshes())
        self.__set_meshes()
        self._set_light()

    # async def __set_meshes(self):
    def __set_meshes(self):
        info('loading track model')
        filename = self.raceprops.gfx_track_path
        if not exists(filename):
            script_path = executable + ' yyagl/build/process_track.py'
            system(script_path + ' assets/tracks/' + self.raceprops.track_name)
        info('loading ' + filename)
        # self.model = await loader.load_model(filename, blocking=False)
        self.model = loader.load_model(filename)
        self.model = P3dNode(self.eng.gfx.gfx_mgr.set_srgb(self.model))
        rpr = self.raceprops
        anim_name = '**/%s*%s*' % (rpr.empty_name, rpr.anim_name)
        for model in self.model.find_all_matches(anim_name):
            # bam files don't contain actor info
            cloned_root = self.__cloned_root(model)
            model_subname = model.name[len(rpr.empty_name):]
            # filenames are like EmptyModelName
            path = '%s/models/%s' % (rpr.track_path, model_subname)
            if '.' in path: path = path.split('.')[0]
            # e.g. desert/Model.001 (Blender appends that)
            self.__set_anim_node(path, cloned_root, model)
            model.remove_node()
        roots = self.model.find_all_matches('**/%s*' % rpr.sign_name)
        self.signs = Signs(roots, rpr.sign_cb)
        self.signs.set_signs()
        list(map(lambda sign: sign.optimize(), roots))
        self.model.optimize()

    @staticmethod
    def __cloned_root(model):
        cloned_root = NodePath(model.name)
        cloned_root.reparent_to(model.parent)
        cloned_root.set_pos(model.get_pos())
        cloned_root.set_hpr(model.hpr)
        cloned_root.set_scale(model.scale)
        return cloned_root

    def __set_anim_node(self, path, cloned_root, model):
        anim_path = '%s-%s' % (path, self.raceprops.anim_name)
        self.__anim_nodes += [AnimNode(path, {'anim': anim_path})]
        self.__anim_nodes[-1].loop('anim')
        self.__anim_nodes[-1].reparent_to(cloned_root)
        self.__anim_nodes[-1].optimize()
        has_omni = model.has_tag(self.raceprops.omni_tag)
        if has_omni and model.get_tag(self.raceprops.omni_tag):
            self.__set_omni(cloned_root)

    def __set_omni(self, root):
        root.set_tag(self.raceprops.omni_tag, 'True')
        a_n = self.__anim_nodes[-1].name
        info('set omni for ' + a_n)
        self.__anim_nodes[-1].set_omni()

    def _set_light(self):
        self.ambient = AmbientLight((.7, .7, .55, 1))
        self.spot_lgt = Spotlight(BitMask32.bit(BitMasks.general))
        self.spot_lgt.set_pos(self.raceprops.shadow_src)
        self.spot_lgt.look_at((0, 0, 0))
        if not self.raceprops.shaders:
            self.spot_lgt.set_color((.2, .2, .2))
        sha = self.eng.gfx.gfx_mgr.shader_support and self.raceprops.shaders
        if sha: self.eng.gfx.gfx_mgr.enable_shader()
        else: self.eng.gfx.gfx_mgr.disable_shader()

    def _destroy_lights(self):
        self.ambient.destroy()
        self.spot_lgt.destroy()

    def update(self, car_pos):
        sh_src = LPoint3f(*self.raceprops.shadow_src)
        self.spot_lgt.set_pos(car_pos + sh_src)

    def redraw_wps(self): pass

    def destroy(self):
        list(map(lambda node: node.destroy(), self.__anim_nodes))
        self.model.remove_node()
        self._destroy_lights()
        self.__anim_nodes = self.__flat_roots = None
        self.signs.destroy()
        self.empty_models = None


class TrackGfxDebug(TrackGfx):

    def __init__(self, mediator, race_props):
        TrackGfx.__init__(self, mediator, race_props)
        self.curr_wp = ''
        self.wp_np = None
        self.wp2txt = {}
        self.eng.attach_obs(self.on_frame)
        self.eng.do_later(2.0, self.redraw_wps)

    def set_curr_wp(self, wayp):
        self.curr_wp = wayp.get_name()[8:]

    def on_frame(self):
        if hasattr(self.mediator, 'phys') and not self.wp2txt:
            for wayp in self.mediator.phys.waypoints:
                self.wp2txt[wayp] = OnscreenText(wayp.get_name()[8:],
                                                 fg=(1, 1, 1, 1), scale=.08)
        if not hasattr(self.mediator, 'phys'): return  # first frame, refactor
        list(map(self.__process_wp, self.mediator.phys.waypoints))

    def __process_wp(self, wayp):
        pos2d = self.eng.gfx.gfx_mgr.pos2d(wayp.node)
        if pos2d:
            self.wp2txt[wayp].show()
            self.wp2txt[wayp].setPos(1.7777 * pos2d[0] + .02,
                                     pos2d[1] + .02)
            # refactor: set_pos doesn't work
            self.wp2txt[wayp]['fg'] = (1, 0, 0, 1) if \
                wayp.get_name()[8:] == self.curr_wp else (1, 1, 1, 1)
        else: self.wp2txt[wayp].hide()

    def redraw_wps(self):
        if not hasattr(self.mediator, 'phys'): return  # first frame, refactor
        if not self.mediator.phys.waypoints: return
        # it may be invoked on track's destruction
        if self.wp_np: self.wp_np.remove_node()
        segs = LineSegs()
        for w_p in self.mediator.phys.waypoints:
            for dest in w_p.prevs:
                segs.moveTo(w_p.pos)
                segs.drawTo(dest.pos)
        segs_node = segs.create()
        self.wp_np = render.attach_new_node(segs_node)

    def destroy(self):
        self.eng.detach_obs(self.on_frame)
        if self.wp_np: self.wp_np = self.wp_np.remove_node()
        list(map(lambda txt: txt.destroy(), self.wp2txt.values()))
        self.wp2txt = self.mediator.phys.waypoints = None
        TrackGfx.destroy(self)


class TrackGfxShader(TrackGfx):

    def update(self, car_pos): pass

    def _set_light(self):
        self.eng.set_amb_lgt((.15, .15, .15, 1))
        self.eng.set_dir_lgt((.8, .8, .8, 1), (-25, -65, 0))

    def _destroy_lights(self): self.eng.clear_lights()


class TrackGfxPbr(TrackGfx):

    def update(self, car_pos): pass

    def _set_light(self):
        self.eng.set_dir_lgt((.8, .8, .8, 1), (-25, -65, 0))

    def _destroy_lights(self): self.eng.clear_lights()

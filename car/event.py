from random import uniform, choice
from itertools import chain
from panda3d.core import Vec3, Vec2
from direct.showbase.InputStateGlobal import inputState
from yyagl.gameobject import EventColleague
from yyagl.computer_proxy import ComputerProxy, once_a_frame
from yyagl.engine.vec import Vec
from yracing.race.event import wpnclasses2id
from yracing.player.player import Player
from yracing.weapon.rocket.rocket import Rocket, RocketNetwork
from yracing.weapon.rear_rocket.rear_rocket import RearRocket, \
    RearRocketNetwork
from yracing.weapon.turbo.turbo import Turbo, TurboNetwork
from yracing.weapon.rotate_all.rotate_all import RotateAll
from yracing.weapon.mine.mine import Mine, MineNetwork


class PlayerKeys:

    def __init__(self, forward, rear, left, right, fire, respawn):
        self.forward = forward
        self.rear = rear
        self.left = left
        self.right = right
        self.fire = fire
        self.respawn = respawn


class Keys:

    def __init__(self, players_keys):
        self.players_keys = players_keys


class DirKeys:

    def __init__(self, forward, rear, left, right):
        self.forward = forward
        self.rear = rear
        self.left = left
        self.right = right

    def __repr__(self):
        return 'forward: %s, rear: %s, left: %s, right: %s' % (
            self.forward, self.rear, self.left, self.right)


class InputBuilder:

    @staticmethod
    def create(state, joystick):  # unused joystick
        if state in ['Waiting', 'Results']:
            inp_bld = InputBuilderAi()
        else:
            inp_bld = InputBuilderPlayer()
        return inp_bld


class InputBuilderAi(InputBuilder):

    @staticmethod
    def build(ai, joystick_mgr, player_car_idx, car_evt):
        # unused joystick_mgr, player_car_idx, car_evt
        return ai.get_input()


class InputBuilderPlayer(InputBuilder):

    @staticmethod
    def build(ai, joystick_mgr, player_car_idx, joystick):
        keys = ['forward', 'rear', 'left', 'right']
        keys = [key + str(player_car_idx) for key in keys]
        if any(inputState.isSet(key) for key in keys):
            return DirKeys(*[inputState.isSet(key) for key in keys])
        jstate = joystick_mgr.get_joystick(player_car_idx)
        # j_bx = joystick_mgr.get_joystick_val(player_car_idx, fire_key)
        # j_by = joystick_mgr.get_joystick_val(player_car_idx, respawn_key)
        # if j_bx and car_evt.mediator.logic.weapon: car_evt.on_fire()
        # if j_by: car_evt.process_respawn()
        fwd = joystick[
            'forward' + str(player_car_idx + 1)]
        rear = joystick[
            'rear' + str(player_car_idx + 1)]
        inp = {'forward': getattr(jstate, fwd),
               'rear': getattr(jstate, rear),
               'left': jstate.x < -.4, 'right': jstate.x > .4}
        keys = ['forward', 'rear', 'left', 'right']
        return DirKeys(*[inp[key] for key in keys])


class CarEvent(EventColleague, ComputerProxy):

    def __init__(self, mediator, race_props, players):
        EventColleague.__init__(self, mediator)
        ComputerProxy.__init__(self)
        self.eng.attach_obs(self.on_collision)
        self.props = race_props
        self._players = players
        self.curr_wpn_id = 0

    def start(self):
        self.eng.attach_obs(self.on_frame)

    def on_collision(self, obj, tgt_obj):
        if obj != self.mediator.gfx.nodepath.p3dnode:
            return
        obj_name = tgt_obj.get_name()
        if obj_name.startswith(self.props.respawn_name):
            self.process_respawn()
        if obj_name.startswith(self.props.pitstop_name):
            self.mediator.phys.apply_damage(True)
            self.mediator.gfx.apply_damage(True)
            self.mediator.event.on_damage(0)
        if obj_name.startswith(self.props.goal_name):
            self._process_goal()
        obst_names = [self.props.wall_name, 'Vehicle']
        if any(obj_name.startswith(name) for name in obst_names):
            self._process_wall()
        if obj_name.startswith(self.props.bonus_name):
            self.on_bonus()
        weapons = ['Mine']
        if any(obj_name.startswith(wpn_name) for wpn_name in weapons):
            int_lat = 10000
            int_rot = 20000
            rndval = lambda: choice([-int_lat, int_lat])
            frc = rndval(), rndval(), 96000
            self.mediator.phys.pnode.apply_central_force(frc)
            torque = choice([-int_rot, int_rot])
            self.mediator.phys.pnode.apply_torque((0, 0, torque))

    def on_bonus(self, cls=None, wpn_id=None):
        if self.mediator.logic.weapon:
            self.mediator.logic.weapon.destroy()
        if cls == 'remove':
            self.mediator.logic.weapon = None
            return cls
        if cls: wpn_cls = cls
        else:
            wpn_classes = [Rocket, RearRocket, Turbo, RotateAll, Mine]
            probs = [.2, .2, .2, .1, .2]
            sel = uniform(0, sum(probs))
            for i, _ in enumerate(wpn_classes):
                if sum(probs[:i]) <= sel <= sum(probs[:i + 1]):
                    wpn_cls = wpn_classes[i]
        part_path = self.props.particle_path
        wpn2path = {
            Rocket: self.props.rocket_path,
            RocketNetwork: self.props.rocket_path,
            RearRocket: self.props.rocket_path,
            RearRocketNetwork: self.props.rocket_path,
            Turbo: self.props.turbo_path,
            TurboNetwork: self.props.turbo_path,
            RotateAll: self.props.rotate_all_path,
            Mine: self.props.mine_path,
            MineNetwork: self.props.mine_path}
        path = wpn2path[wpn_cls]
        car_names = [player.car for player in self._players]
        self.mediator.logic.weapon = wpn_cls(
            self.mediator, path, car_names, part_path,
            wpn_id or self.curr_wpn_id, self._players)
        self.curr_wpn_id += 1
        self.mediator.logic.weapon.attach_obs(self.on_rotate_all)
        return wpn_cls

    def on_rotate_all(self, sender):
        self.notify('on_rotate_all', sender)

    def _on_crash(self):
        if self.mediator.fsm.getCurrentOrNextState() != 'Results':
            self.mediator.gfx.crash_sfx()

    def _process_wall(self):
        self._on_crash()

    def _process_goal(self):
        is_res = self.mediator.fsm.getCurrentOrNextState() == 'Results'
        has_started = self.mediator.logic.lap_time_start
        is_corr = self.mediator.logic.correct_lap
        if is_res or has_started and not is_corr:
            return
        self.mediator.logic.reset_waypoints()
        lap_times = self.mediator.logic.lap_times
        if self.mediator.logic.lap_time_start:
            lap_times += [self.mediator.logic.lap_time]
            self._process_nonstart_goals(1 + len(lap_times),
                                         self.mediator.laps)
        self.mediator.logic.lap_time_start = self.eng.curr_time

    def _process_nonstart_goals(self, lap_number, laps):
        pass

    def process_respawn(self):
        last_wp = self.mediator.logic.last_wp
        start_wp_n, end_wp_n = last_wp.prev, last_wp.next
        spos = start_wp_n.pos
        height = self.mediator.phys.gnd_height(start_wp_n.pos)
        spos = Vec(spos.x, spos.y, height + 2)
        self.mediator.gfx.nodepath.set_pos(spos)
        endpos = end_wp_n.node.get_pos(start_wp_n.node)
        wp_vec = Vec(endpos.x, endpos.y, 0).normalize()
        or_h = (wp_vec.xy).signed_angle_deg(Vec2(0, 1))
        self.mediator.gfx.nodepath.set_hpr((-or_h, 0, 0))
        self.mediator.gfx.nodepath.p3dnode.set_linear_velocity(0)
        self.mediator.gfx.nodepath.p3dnode.set_angular_velocity(0)

    def on_frame(self):
        _input = self._get_input()
        states = ['Loading', 'Countdown']
        if self.mediator.fsm.getCurrentOrNextState() in states:
            _input = DirKeys(*[False for _ in range(4)])
            self.mediator.logic.reset_car()
        self.__update_contact_pos()
        self.mediator.phys.update_car_props()
        self.mediator.logic.update_waypoints()
        self.mediator.logic.update(_input)
        if self.mediator.logic.is_upside_down:
            self.mediator.gfx.nodepath.set_r(0)

    def __update_contact_pos(self):
        p3dpos = self.mediator.pos + (0, 0, 50)
        top = Vec(p3dpos.x, p3dpos.y, p3dpos.z)
        p3dpos = self.mediator.pos + (0, 0, -50)
        bottom = Vec(p3dpos.x, p3dpos.y, p3dpos.z)
        hits = self.eng.phys_mgr.ray_test_all(top, bottom).get_hits()
        r_n = self.props.road_name
        for hit in [hit for hit in hits if r_n in hit.get_node().get_name()]:
            self.mediator.logic.last_wp = self.mediator.logic.closest_wp()

    def on_damage(self, level):
        pass

    def destroy(self):
        list(map(self.eng.detach_obs, [self.on_collision, self.on_frame]))
        EventColleague.destroy(self)
        ComputerProxy.destroy(self)


class CarPlayerEvent(CarEvent):

    def __init__(self, mediator, race_props, players):
        CarEvent.__init__(self, mediator, race_props, players)
        keys = race_props.keys.players_keys[mediator.player_car_idx]
        suff = str(mediator.player_car_idx)
        self.label_events = [
            ('forward' + suff, keys.forward), ('left' + suff, keys.left),
            ('rear' + suff, keys.rear), ('right' + suff, keys.right)]
        watch = inputState.watchWithModifiers
        self.toks = list(map(
            lambda args: watch(args[0], self.eng.lib.remap_code(args[1])),
            self.label_events))  # arg = (lab, evt)
        if not self.eng.is_runtime:
            self.accept('f11', self.mediator.gui.pars.toggle)
            self.accept('f2', self.eng.gfx.gfx_mgr.screenshot)
            suff = str(8 + mediator.player_car_idx)
            self.accept('f' + suff, self._process_end_goal)
        state = self.mediator.fsm.getCurrentOrNextState()
        player_car_names = [player.car for player in self._players
                            if player.kind == Player.human]
        joystick = \
            self.mediator._car_props.name == \
                player_car_names[mediator.player_car_idx] and \
            mediator.player_car_idx < \
                self.eng.joystick_mgr.joystick_lib.num_joysticks
        # access to a protected member
        self.input_bld = InputBuilder.create(state, joystick)
        keys = self.props.keys.players_keys[mediator.player_car_idx]
        self.accept(self.eng.lib.remap_str(keys.respawn), self.process_respawn)
        evtrespawn = self.props.joystick['respawn' + \
            str(mediator.player_car_idx + 1)]
        evtrespawn = 'joypad' + str(mediator.player_car_idx) + '-' + evtrespawn + '-up'
        self.accept(evtrespawn, self.process_respawn)
        # self.eng.do_later(5, lambda: self.on_bonus(Turbo) and None)

    def on_frame(self):
        CarEvent.on_frame(self)
        self.mediator.logic.camera.update(
            self.mediator.phys.speed_ratio, self.mediator.logic.is_rolling,
            self.mediator.fsm.getCurrentOrNextState() == 'Countdown',
            self.mediator.logic.is_rotating)
        self.mediator.audio.update(self.mediator.logic.is_skidmarking,
                                   self.mediator.phys.lin_vel_ratio,
                                   self._get_input(),
                                   self.mediator.logic.is_drifting,
                                   self.mediator.phys.is_flying,
                                   self.mediator.logic.is_rolling)

    def on_collision(self, obj, tgt_obj):
        CarEvent.on_collision(self, obj, tgt_obj)
        if obj != self.mediator.gfx.nodepath.p3dnode:
            return
        obj_name = tgt_obj.get_name()
        if any(obj_name.startswith(s) for s in self.props.roads_names):
            self.mediator.audio.landing_sfx.play()
        if obj_name.startswith(self.props.pitstop_name):
            self.mediator.gui.panel.apply_damage(True)
            self.mediator.gfx.set_decorator('pitstop')
            self.mediator.audio.pitstop_sfx.play()
        if 'Rocket' in obj_name:
            if obj != tgt_obj.get_python_tag('car').phys.pnode:
                self.mediator.audio.rocket_hit_sfx.play()
        if any(wpnname in obj_name for wpnname in ['Rocket', 'Mine']):
            self.eng.joystick_mgr.joystick_lib.set_vibration(
                self.mediator.player_car_idx, 'crash', .8)

    def on_bonus(self, cls=None, wpn_id=None):
        if self.mediator.logic.weapon: self.mediator.gui.panel.unset_weapon()
        cls = CarEvent.on_bonus(self, cls)
        evtfire = self.props.joystick[
            'fire' + str(self.mediator.player_car_idx + 1)]
        evtfire = 'joypad' + str(self.mediator.player_car_idx) + '-' + evtfire + '-up'
        if cls == 'remove':
            keys = self.props.keys.players_keys[self.mediator.player_car_idx]
            self.ignore(keys.fire)
            self.ignore(evtfire)
            return
        if not cls: return  # if removing
        keys = self.props.keys.players_keys[self.mediator.player_car_idx]
        self.accept(self.eng.lib.remap_str(keys.fire), self.on_fire)
        self.accept(evtfire, self.on_fire)
        if self.mediator.fsm.getCurrentOrNextState() != 'Waiting':
            self.mediator.gui.panel.set_weapon(
                self.props.season_props.wpn2img[cls.__name__])
        return cls

    def on_fire(self):
        keys = self.props.keys.players_keys[self.mediator.player_car_idx]
        # self.ignore(keys.fire)
        evtfire = self.props.joystick[
            'fire' + str(self.mediator.player_car_idx + 1)]
        evtfire = 'joypad' + str(self.mediator.player_car_idx) + '-' + evtfire + '-up'
        self.ignore(evtfire)
        self.mediator.logic.fire()
        self.mediator.gui.panel.unset_weapon()
        self.ignore(keys.fire)

    def _process_wall(self):
        CarEvent._process_wall(self)
        self.mediator.audio.crash_sfx.play()
        self.eng.joystick_mgr.joystick_lib.set_vibration(
            self.mediator.player_car_idx, 'crash', .5)

    def _process_nonstart_goals(self, lap_number, laps):
        CarEvent._process_nonstart_goals(self, lap_number, laps)
        curr_lap = min(laps, lap_number)
        self.mediator.gui.panel.lap_txt.setText(str(curr_lap)+'/'+str(laps))
        self.mediator.audio.lap_sfx.play()

    def _process_end_goal(self):
        self.mediator.fsm.demand('Waiting')
        self.notify('on_end_race', self.mediator.name)

    def _process_goal(self):
        CarEvent._process_goal(self)
        logic = self.mediator.logic
        is_best = not logic.lap_times or min(logic.lap_times) > logic.lap_time
        if logic.lap_time_start and (not logic.lap_times or is_best):
            self.mediator.gui.panel.best_txt.setText(
                self.mediator.gui.panel.time_txt.getText())
        if len(logic.lap_times) == self.mediator.laps:
            self._process_end_goal()
        # self.on_bonus()  # to test weapons

    @once_a_frame
    def _get_input(self):
        player_car_idx = self.mediator.player_car_idx
        joystick_mgr = self.eng.joystick_mgr
        return self.input_bld.build(
            self.mediator.ai, joystick_mgr, player_car_idx,
            self.props.joystick)

    def destroy(self):
        evtfire = self.props.joystick[
            'fire' + str(self.mediator.player_car_idx + 1)]
        evtfire = 'joypad' + str(self.mediator.player_car_idx) + '-' + evtfire + '-up'
        evtrespawn = self.props.joystick['respawn' + \
            str(self.mediator.player_car_idx + 1)]
        evtrespawn = 'joypad' + str(self.mediator.player_car_idx) + '-' + evtrespawn + '-up'
        keys = self.props.keys.players_keys[self.mediator.player_car_idx]
        evts = ['f11', 'f8', 'f2', keys.fire, keys.respawn, evtfire, evtrespawn]
        list(map(lambda tok: tok.release(), self.toks))
        list(map(self.ignore, evts))
        CarEvent.destroy(self)


class CarPlayerEventServer(CarPlayerEvent):

    def _process_end_goal(self):
        self.eng.client.send(['end_race_player'])
        CarPlayerEvent._process_end_goal(self)


class CarPlayerEventClient(CarPlayerEvent):

    def __init__(self, mediator, race_props, players):
        CarPlayerEvent.__init__(self, mediator, race_props, players)
        self.last_sent = self.eng.curr_time

    def on_frame(self):
        CarPlayerEvent.on_frame(self)
        pos = self.mediator.pos
        gfx = self.mediator.gfx
        vehicle = self.mediator.phys.vehicle
        fwd = render.get_relative_vector(gfx.nodepath.node, Vec3(0, 1, 0))
        velocity = vehicle.get_chassis().get_linear_velocity()
        ang_vel = vehicle.get_chassis().get_angular_velocity()
        curr_inp = self._get_input()
        inp = [curr_inp.forward, curr_inp.rear, curr_inp.left, curr_inp.right]
        eng_frc = vehicle.get_wheel(0).get_engine_force()
        brk_frc_fwd = vehicle.get_wheel(0).get_brake()
        brk_frc_rear = vehicle.get_wheel(2).get_brake()
        steering = vehicle.get_steering_value(0)
        level = 0
        curr_chassis = gfx.nodepath.node.get_children()[0]
        if gfx.chassis_np_low.name in curr_chassis.get_name():
            level = 1
        if gfx.chassis_np_hi.name in curr_chassis.get_name():
            level = 2
        wpn = ''
        wpn_id = 0
        wpn_pos = (0, 0, 0)
        wpn_fwd = (0, 0, 0)
        if self.mediator.logic.weapon:
            curr_wpn = self.mediator.logic.weapon
            wpn_id = curr_wpn.id
            wpn = wpnclasses2id[curr_wpn.__class__]
            wnode = curr_wpn.gfx.gfx_np.node
            wpn_pos = wnode.get_pos(render)
            wpn_fwd = render.get_relative_vector(wnode, Vec3(0, 1, 0))
        packet = list(chain(
            ['player_info', self.eng.client.myid], pos, fwd, velocity,
            ang_vel, inp, [eng_frc, brk_frc_fwd, brk_frc_rear, steering],
            [level], [wpn, wpn_id], wpn_pos, wpn_fwd))
        packet += [len(self.mediator.logic.fired_weapons)]
        for i in range(len(self.mediator.logic.fired_weapons)):
            curr_wpn = self.mediator.logic.fired_weapons[i]
            wpn = wpnclasses2id[curr_wpn.__class__]
            wnode = curr_wpn.gfx.gfx_np.node
            wpn_pos = wnode.get_pos(render)
            wpn_fwd = render.get_relative_vector(wnode, Vec3(0, 1, 0))
            packet += chain([wpn, curr_wpn.id], wpn_pos, wpn_fwd)
        if self.eng.curr_time - self.last_sent > self.eng.client.rate:
            self.eng.client.send_udp(packet, self.eng.client.myid)
            self.last_sent = self.eng.curr_time

    def _process_end_goal(self):
        self.eng.client.send(['end_race_player'])
        CarPlayerEvent._process_end_goal(self)


class CarNetworkEvent(CarEvent):

    @once_a_frame
    def _get_input(self):
        return self.mediator.logic.curr_network_input

    def on_bonus(self, wpn_cls=None):  # parameters differ from overridden
        pass

    def set_fired_weapon(self):
        self.mediator.logic.fire()

    def unset_fired_weapon(self, wpn):
        self.mediator.logic.unset_fired_weapon(wpn)

    def set_weapon(self, wpn_cls, wpn_id):
        # if wpn_code:
        #     wpncode2cls = {
        #         'rocket': Rocket, 'rearrocket': RearRocket, 'turbo': Turbo,
        #         'rotateall': RotateAll, 'mine': Mine}
        #     wpn_cls = wpncode2cls[wpn_code]
        # else:
        #     wpn_cls = None
        CarEvent.on_bonus(self, wpn_cls, wpn_id)

    def unset_weapon(self):
        self.mediator.logic.weapon.destroy()
        self.mediator.logic.weapon = None


class CarAiEvent(CarEvent):

    @once_a_frame
    def _get_input(self):
        return self.mediator.ai.get_input()


class CarAiPlayerEvent(CarAiEvent, CarPlayerEvent):

    pass

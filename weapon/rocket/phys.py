from panda3d.bullet import BulletSphereShape
from yracing.weapon.weapon.phys import RocketWeaponPhys


class RocketPhys(RocketWeaponPhys):

    coll_mesh_cls = BulletSphereShape
    joint_z = .8
    gfx_dz = 0
    launch_dist = 3.5
    rot_deg = 0
    rocket_coll_name = 'Rocket'

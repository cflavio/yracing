from panda3d.core import BitMask32
from panda3d.bullet import BulletBoxShape, BulletGhostNode
from yyagl.gameobject import PhysColleague
from yyagl.engine.vec import Vec
from yracing.bitmasks import BitMasks


class BonusPhys(PhysColleague):

    def __init__(self, mediator, pos):
        self.pos = pos
        self.ghost = None
        PhysColleague.__init__(self, mediator)
        self.ghost = BulletGhostNode('Bonus')
        self.ghost.add_shape(BulletBoxShape((1, 1, 2.5)))
        ghost_np = self.eng.attach_node(self.ghost)
        pos = self.pos
        pos = Vec(pos.x, pos.y, pos.z)
        ghost_np.set_pos(pos)
        ghost_np.set_collide_mask(BitMask32.bit(BitMasks.ghost))
        self.eng.phys_mgr.attach_ghost(self.ghost)

    def destroy(self):
        self.ghost = self.eng.phys_mgr.remove_ghost(self.ghost)
        PhysColleague.destroy(self)

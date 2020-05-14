from yracing.weapon.weapon.event import WeaponEvent


class MineEvent(WeaponEvent):

    def on_collision(self, obj, tgt_obj):  # unused obj
        if tgt_obj.get_name() == self.mediator.phys.coll_name:
            self._on_coll_success()

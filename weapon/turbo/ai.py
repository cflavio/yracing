from yracing.weapon.weapon.ai import WeaponAi


class TurboAi(WeaponAi):

    def update(self):
        if self.is_fired_or_before: return False
        closest_center, closest_left, closest_right = self.obstacles
        return closest_center.dist > 40

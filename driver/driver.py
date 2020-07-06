from yyagl.gameobject import GameObject


class Driver(GameObject):

    def __init__(self, img_idx, name, speed, adherence, stability):
        GameObject.__init__(self)
        self.img_idx = img_idx
        self.name = name
        self.speed = speed
        self.adherence = adherence
        self.stability = stability

    def __repr__(self):
        return 'driver(%s %s %s %s %s)' % (
            self.img_idx, self.name, self.speed, self.adherence,
            self.stability)

    def to_json(self):
        return {
            'img_idx': self.img_idx, 'name': self.name, 'speed': self.speed,
            'adherence': self.adherence, 'stability': self.stability}

    @staticmethod
    def from_json(dct):
        return Driver(
            dct['img_idx'], dct['name'], dct['speed'], dct['adherence'],
            dct['stability'])

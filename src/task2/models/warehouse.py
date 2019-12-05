from PyQt5 import Qt


class Warehouse:
    type = 3
    color = Qt.darkRed

    def __init__(
            self,
            idx=None,
            name=None,
            armor=None,
            armor_capacity=None,
            replenishment=None,
    ):
        self.idx = idx
        self.name = name
        self.armor = armor
        self.armor_capacity = armor_capacity
        self.replenishment = replenishment

    def __str__(self):
        return '\n'.join((
            f'Point idx: {self.idx}',
            f'Name: {self.name}',
            f'Armor: {self.armor}, capacity: {self.armor_capacity}',
            f'Replenishment: {self.replenishment}'
        ))

    @classmethod
    def from_dict(cls, d):
        if cls.type != d['type']:
            raise ValueError(f"Incorrect type in {cls.__name__}")
        return cls(
            idx=d['point_idx'],
            name=d['name'],
            armor=d['armor'],
            armor_capacity=d['armor_capacity'],
            replenishment=d['replenishment'],
        )
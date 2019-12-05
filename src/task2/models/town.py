from PyQt5 import Qt


class Town:
    type = 1
    color = Qt.darkGreen

    def __init__(
            self,
            idx=None,
            name=None,
            level=None,
            next_level_price=None,
            population=None,
            population_capacity=None,
            product=None,
            product_capacity=None,
            armor=None,
            armor_capacity=None,
            player_idx=None,
    ):
        self.idx = idx
        self.name = name
        self.level = level
        self.next_level_price = next_level_price
        self.population = population
        self.population_capacity = population_capacity
        self.product = product
        self.product_capacity = product_capacity
        self.armor = armor
        self.armor_capacity = armor_capacity
        self.player_idx = player_idx

    def __str__(self):
        return '\n'.join((
            f'Point idx: {self.idx}',
            f'Name: {self.name}',
            f'Level: {self.level}, next level price: {self.next_level_price}',
            f'Population: {self.population}, capacity: {self.population_capacity}',
            f'Product: {self.product}, capacity: {self.product_capacity}',
            f'Armor: {self.armor}, capacity: {self.armor_capacity}',
            f'Player idx: {self.player_idx}',
        ))

    @classmethod
    def from_dict(cls, d):
        if cls.type != d['type']:
            raise ValueError(f"Incorrect type in {cls.__name__}")
        return cls(
            idx=d['idx'],
            name=d['name'],
            level=d['level'],
            next_level_price=d['next_level_price'],
            population=d['population'],
            population_capacity=d['population_capacity'],
            product=d['product'],
            product_capacity=d['product_capacity'],
            armor=d['armor'],
            armor_capacity=d['armor_capacity'],
            player_idx=d['player_idx']
        )
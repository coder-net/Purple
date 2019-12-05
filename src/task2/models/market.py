from PyQt5 import Qt


class Market:
    type = 2
    color = Qt.yellow

    def __init__(
            self,
            idx=None,
            name=None,
            product=None,
            product_capacity=None,
            replenishment=None,
            events=None
    ):
        self.idx = idx
        self.name = name
        self.product = product
        self.product_capacity = product_capacity
        self.replenishment = replenishment
        self.events = events

    def __str__(self):
        return '\n'.join((
            f'Point idx: {self.idx}',
            f"Market name: {self.name}",
            f'Product: {self.product}, capacity: {self.product_capacity}',
            f'Replenishment: {self.replenishment}',
            f'Events: {self.events if self.events else "None"}',
        ))

    @classmethod
    def from_dict(cls, d):
        if cls.type != d['type']:
            raise ValueError(f'Incorrect type in {cls.__name__}')
        return cls(
            idx=d['point_idx'],
            name=d['name'],
            product=d['product'],
            product_capacity=d['product_capacity'],
            replenishment=d['replenishment'],
            events=d['events']
        )
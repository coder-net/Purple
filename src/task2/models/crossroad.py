from PyQt5 import Qt


class Crossroad:
    type = 0
    color = Qt.gray

    def __init__(self, idx):
        self.idx = idx

    def __str__(self):
        return f'Point idx: {self.idx}'
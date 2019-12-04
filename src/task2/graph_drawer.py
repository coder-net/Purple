from PyQt5.QtWidgets import (QWidget, QLabel,
                             QLineEdit, )
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, QPoint


buildings_to_info = {
    0: ('Crossroad', Qt.gray),
    1: ('Town', Qt.darkGreen),
    2: ('Market', Qt.yellow),
    3: ('Warehouse', Qt.darkRed),
}


class GraphDrawer(QWidget):
    def __init__(self):
        super().__init__()
        self.graph = None
        self.buildings = None
        self.padding = 50
        self.idx_to_building = {}
        self.points_to_labels = {}
        self.edges_to_weights = {}
        self.zoom = 1
        self.delta = QPoint(0, 0)
        self.start = self.delta
        self.is_visible_weight = False
        self.pressing = False
        self.initUI()

    def initUI(self):
        self.show()

    def cameraToHome(self):
        if self.graph:
            self.zoom = 1
            self.delta = QPoint(0, 0)
            self.start = self.delta
            self.update()

    # TODO, change
    def initLabels(self):
        d = min(int(self.padding * 1.5),
                int(self.graph.shortest_edge / 2 * min(self.height(), self.width())))
        for point in self.graph.points:
            self.idx_to_building[point.idx] = Town(point.idx, d // 2, self)
        color = self.palette().color(self.backgroundRole()).name()
        for edge in self.graph.edges:
            self.edges_to_weights[edge.idx] = CustomLabel(
                str(edge.weight), self, color)
            self.edges_to_weights[edge.idx].lower()
            self.edges_to_weights[edge.idx].show()

    def deleteLabels(self):
        for widget in self.idx_to_building.values():
            widget.setParent(None)
        self.idx_to_building.clear()
        for label in self.edges_to_weights.values():
            label.setParent(None)
        self.edges_to_weights.clear()

    def setWeightLabelsVisible(self, flag):
        self.is_visible_weight = flag
        for label in self.edges_to_weights.values():
            label.setVisible(flag)
        self.update()

    def setGraph(self, graph):
        self.graph = graph
        self.deleteLabels()
        self.initLabels()
        self.is_visible_weight = True
        self.update()

    # TODO, change
    def setBuildings(self, buildings):
        self.buildings = buildings
        for building in self.buildings['posts']:
            idx = building['point_idx']
            if idx in self.idx_to_building:
                self.idx_to_building[idx].setTownInfo(town_type=building['type'])

    def paintEvent(self, e):
        if self.graph:
            painter = QPainter()
            painter.begin(self)
            painter.scale(self.zoom, self.zoom)
            painter.translate(self.delta)

            self.delta.setX = self.start.x()
            self.delta.setY = self.start.y()

            # how scale normalized coordinates
            map_x = self.width() - 2 * self.padding
            map_y = self.height() - 2 * self.padding
            pos = self.graph.pos

            # TODO, delete this
            # choose suitable node size
            d = min(int(self.padding * 1.5),
                    int(self.graph.shortest_edge / 2 * min(map_x, map_y)))
            # choose suitable font size
            weight_font_size = int(1 / self.graph.biggest_idx_len * d)
            if weight_font_size <= 0:
                weight_font_size = 1

            painter.setPen(QPen(Qt.black, 1 / self.zoom))

            for edge in self.graph.edges:
                p1, p2 = edge.points
                x1, y1, x2, y2 = (
                    pos[p1][0] * map_x + self.padding,
                    pos[p1][1] * map_y + self.padding,
                    pos[p2][0] * map_x + self.padding,
                    pos[p2][1] * map_y + self.padding
                )
                painter.drawLine(x1, y1, x2, y2)
                lbl = self.edges_to_weights[edge.idx]
                lbl.setFontSize(weight_font_size)
                lbl.move(
                    self.zoom * (x1 + (x2 - x1) // 2 + self.delta.x()) - lbl.width() // 2,
                    self.zoom * (y1 + (y2 - y1) // 2 + self.delta.y()) - lbl.height() // 2
                )

            # painter.setPen(QPen(Qt.gray))
            #
            # painter.setBrush(QBrush(Qt.gray))

            for idx, (x, y) in pos.items():
                x = int(x * map_x) + self.padding
                y = int(y * map_y) + self.padding

                building = self.idx_to_building[idx]
                building.scale = self.zoom
                building.move(self.zoom * (x + self.delta.x()) - building.width() // 2,
                              self.zoom * (y + self.delta.y()) - building.height() // 2)

            painter.end()

    def wheelEvent(self, event):
        self.zoom += event.angleDelta().y() / 2880
        self.update()

    def mousePressEvent(self, QMouseEvent):
        self.start = QMouseEvent.pos() - self.delta
        self.pressing = True

    def mouseMoveEvent(self, QMouseEvent):
        if self.pressing:
            end = QMouseEvent.pos()
            self.delta = (end - self.start)
            self.update()

    def mouseReleaseEvent(self, QMouseEvent):
        self.pressing = False


class CustomLabel(QLabel):
    def __init__(self, text, parent, background_color=None):
        super().__init__(text, parent)
        if background_color:
            self.setStyleSheet(
                f"QLabel {{background-color: {background_color};}}")

    def setFontSize(self, font_size):
        font = self.font()
        font.setPointSize(font_size)
        self.setFont(font)
        self.resize(self.sizeHint())


class Town(QWidget):
    def __init__(self, idx, radius, parent=None, font_size=None):
        super().__init__(parent)

        self.town_idx = idx
        self.town_type = 0
        self.font_coefficient = 1.5
        self.idx_label = CustomLabel(str(idx), self)
        self._outer_radius = radius
        self._inner_radius = int(radius * 0.8)  # ? property
        self._font_size = font_size or int(1 / len(str(idx)) * self._inner_radius * self.font_coefficient)
        self._scale = 0
        self.thickness = 2
        self.setTownInfo()
        self.show()

    @property
    def outer_radius(self):
        return int(self.scale * self._outer_radius) + 1

    @property
    def inner_radius(self):
        return int(self.scale * self._inner_radius) + 1

    @property
    def font_size(self):
        return int(self.scale * self._font_size) + 1

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        self.resize((self.outer_radius + self.thickness + 1) * 2, (self.outer_radius + self.thickness + 1) * 2)

    def paintEvent(self, e):
        inner_radius = self.inner_radius
        outer_radius = self.outer_radius
        font_size = self.font_size

        painter = QPainter()
        painter.begin(self)

        painter.setPen(QPen(Qt.black, self.thickness))

        painter.drawEllipse(self.thickness, self.thickness, 2 * outer_radius, 2 * outer_radius)

        _, color = buildings_to_info[self.town_type]
        painter.setBrush(color)

        diff = outer_radius - inner_radius
        painter.drawEllipse(diff + self.thickness, diff + self.thickness, 2 * inner_radius, 2 * inner_radius)

        self.idx_label.setFontSize(font_size)
        self.idx_label.move(outer_radius - self.idx_label.width() // 2, outer_radius - self.idx_label.height() // 2)

        painter.end()

    def setTownInfo(self, idx=None, town_type=None,):
        self.town_idx = idx or self.town_idx
        self.town_type = town_type or self.town_type

        self.setToolTip(f'Idx: {self.town_idx}\nType: {buildings_to_info[self.town_type][0]}')

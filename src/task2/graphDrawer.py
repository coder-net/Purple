from PyQt5.QtWidgets import (QWidget, QLabel,
                             QLineEdit,)
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, QPoint

buildings_color_by_type = {'Town': Qt.red,
                           'Market': Qt.green, 'Warehouse': Qt.darkBlue}
buildings_name_by_number_type = ['Town', 'Market', 'Warehouse']


class GraphDrawer(QWidget):

    def __init__(self):
        super().__init__()
        self.graph = None
        self.buildings = None
        self.padding = 50
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

    def setToolTips(player):
        pass

    def initLabels(self):
        for point in self.graph.points:
            self.points_to_labels[point.idx] = CustomLabel(
                str(point.idx), self)
            self.points_to_labels[point.idx].show()
        color = self.palette().color(self.backgroundRole()).name()
        for edge in self.graph.edges:
            self.edges_to_weights[edge.idx] = CustomLabel(
                str(edge.weight), self, color)
            self.edges_to_weights[edge.idx].lower()
            self.edges_to_weights[edge.idx].show()

    def deleteLabels(self):
        for label in self.points_to_labels.values():
            label.setParent(None)
        self.points_to_labels.clear()
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

    def setBuildings(self, buildings):
        self.buildings = buildings

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

            # choose suitable node size
            d = min(int(self.padding * 1.5),
                    int(self.graph.shortest_edge / 2 * min(map_x, map_y)))
            # choose suitable font size
            weight_font_size = int(1 / self.graph.biggest_idx_len * d)
            node_font_size = int(
                1 / self.graph.biggest_idx_len * d * self.zoom)
            # qlabel's font size must be greater than 0
            if weight_font_size <= 0:
                weight_font_size = 1
                if node_font_size <= 0:
                    node_font_size = 1

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

            painter.setPen(QPen(Qt.gray))

            painter.setBrush(QBrush(Qt.gray))

            for idx, (x, y) in pos.items():
                x = int(x * map_x) + self.padding
                y = int(y * map_y) + self.padding

                self.setDrawColorForBuildings(painter, idx)
                painter.drawEllipse(x - d // 2, y - d // 2, d, d)
                lbl = self.points_to_labels[idx]
                lbl.setFontSize(node_font_size)
                lbl.move(self.zoom * (x + self.delta.x()) - lbl.width() // 2,
                         self.zoom * (y + self.delta.y()) - lbl.height() // 2)

            painter.end()

    def setDrawColorForBuildings(self, painter, idx):
        color = Qt.gray
        for building in self.buildings['posts']:
            if building['point_idx'] == idx:
                name = buildings_name_by_number_type[building['type'] - 1]
                color = buildings_color_by_type[name]
        painter.setBrush(QBrush(color))

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

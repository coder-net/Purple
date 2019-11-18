import sys
import os
from PyQt5.QtWidgets import (QWidget, QApplication, QLabel, QFileDialog, QPushButton, QLineEdit, QGridLayout,
                             QVBoxLayout)
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, QPoint
from utils import graph_from_json


class Application(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # TODO: main window to center
        self.setGeometry(500, 500, 1000, 800)
        file_label = QLabel("file", self)
        file_label.resize(file_label.sizeHint())

        # why
        file_label.move(20, 5)
        file_label.setToolTip('end file ')
        self.filePath = QLineEdit("Select file", self)
        self.filePath.setObjectName("file")
        self.filePath.resize(self.filePath.sizeHint())
        self.filePath.move(120, 5)
        self.filePath.setToolTip('Select file')

        # const size bad
        file_select_button = QPushButton('Select file', self)
        file_select_button.resize(file_select_button.sizeHint())
        file_select_button.move(300, 5)
        file_select_button.clicked.connect(self.selectFile)

        home_button = QPushButton('Home', self)
        home_button.resize(home_button.sizeHint())
        home_button.clicked.connect(self.cameraToHome)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.addWidget(file_label, 1, 1)
        grid.addWidget(self.filePath, 1, 2)
        grid.addWidget(file_select_button, 1, 3)
        grid.addWidget(home_button, 1, 0)

        verticalLayout = QVBoxLayout()
        verticalLayout.setSpacing(0)
        graph_drawer = GraphDrawer()
        graph_drawer.resize(500, 500)
        self.graphWidget = graph_drawer
        verticalLayout.addLayout(grid)
        verticalLayout.addWidget(self.graphWidget)
        self.setLayout(verticalLayout)
        self.show()

    # TODO, error handing, if file not chosen
    def selectFile(self):
        self.filePath.setText(QFileDialog.getOpenFileName()[0])
        self.graphWidget.graph = graph_from_json(self.filePath.text())
        if len(self.graphWidget.points_labels) > 0:
            for idx in self.graphWidget.points_labels:
                self.graphWidget.points_labels[idx].hide()
            self.graphWidget.points_labels.clear()
        self.graphWidget.initLabels()

    # TODO: incapsulate
    def cameraToHome(self):
        if self.graphWidget.graph:
            self.graphWidget.zoom = 1
            self.graphWidget.delta = QPoint(0, 0)
            self.graphWidget.start = self.graphWidget.delta
            self.graphWidget.update()


class GraphDrawer(QWidget):
    def __init__(self):
        super().__init__()
        self.graph = None
        self.padding = 100
        # TODO: rename points_to_labels
        self.points_labels = {}
        self.zoom = 1
        self.delta = QPoint(0, 0)
        self.start = self.delta
        self.pressing = False
        self.initUI()

    def initUI(self):
        # self.setGeometry(500, 500, self.width() // 2, self.height() // 2)
        self.setWindowTitle('Graph visualization')
        self.show()

    def initLabels(self):
        for point in self.graph.points:
            idx = point.idx
            self.points_labels[idx] = QLabel(str(idx), self)
            self.points_labels[idx].show()

    def paintEvent(self, e):
        if self.graph:
            painter = QPainter()
            painter.begin(self)
            painter.scale(self.zoom, self.zoom)
            painter.translate(self.delta)

            self.delta.setX = self.start.x()
            self.delta.setY = self.start.y()

            x_coef = self.width() - 2 * self.padding
            y_coef = self.height() - 2 * self.padding
            pos = self.graph.pos

            for edge in self.graph.edges:
                p1, p2 = edge.points
                painter.drawLine(
                    pos[p1][0] * x_coef + self.padding,
                    pos[p1][1] * y_coef + self.padding,
                    pos[p2][0] * x_coef + self.padding,
                    pos[p2][1] * y_coef + self.padding
                )

            painter.setBrush(QBrush(Qt.gray))
            painter.setPen(QPen(Qt.gray))

            r = min(int(self.padding * 1.5), int(self.graph.shortest_edge / 2 * min(x_coef, y_coef)))
            font_size = int(1 / len(str(self.graph.biggest_idx)) * r * 1.)
            if font_size <= 0:
                font_size = 1

            for idx, (x, y) in pos.items():
                x = int(x * x_coef) + self.padding
                y = int(y * y_coef) + self.padding
                painter.drawEllipse(x - r // 2, y - r // 2, r, r)
                lbl = self.points_labels[idx]
                font = lbl.font()
                font.setPointSize(font_size * self.zoom)
                lbl.setFont(font)
                lbl.adjustSize()
                lbl.move(self.zoom * (x + self.delta.x()) - lbl.width() // 2,
                         self.zoom * (y + self.delta.y()) - lbl.height() // 2)

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Application()
    sys.exit(app.exec_())

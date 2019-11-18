import sys
import os.path
from PyQt5.QtWidgets import (QWidget, QApplication, QLabel, QFileDialog,
                             QPushButton, QLineEdit, QGridLayout,
                             QVBoxLayout, QDesktopWidget)
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, QPoint
from utils import graph_from_json


class Application(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # TODO: main window to center
        self.setWindowTitle('Graph visualization')
        self.resize(900, 600)
        self.toCenter()

        file_label = QLabel("filename:", self)
        file_label.resize(file_label.sizeHint())

        file_label.move(20, 5)
        file_label.setToolTip('end file ')
        self.filePath = QLineEdit("Select file", self)
        self.filePath.setObjectName("file")
        self.filePath.resize(self.filePath.sizeHint())
        self.filePath.move(120, 5)
        self.filePath.setToolTip('Select file')

        file_select_button = QPushButton('Select file', self)
        file_select_button.resize(file_select_button.sizeHint())
        file_select_button.move(300, 5)

        home_button = QPushButton('Home', self)
        home_button.resize(home_button.sizeHint())

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

        home_button.clicked.connect(self.graphWidget.cameraToHome)
        file_select_button.clicked.connect(self.selectFile)

        self.show()

    def toCenter(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # TODO, error handing, if file not chosen
    def selectFile(self):
        self.filePath.setText(QFileDialog.getOpenFileName()[0])
        filename = self.filePath.text()
        if not os.path.isfile(filename):
            self.fileSelectError('No such file')
            return

        _, extension = os.path.splitext(filename)
        if extension != '.json':
            self.fileSelectError('Extension is incorrect. Must be ".json"')
            return

        try:
            graph = graph_from_json(self.filePath.text())
            self.graphWidget.setGraph(graph)
            self.graphWidget.setWeightLabelsVisible(False)
        except:
           self.fileSelectError('Incorrect structure of file')

    def fileSelectError(self, msg):
        self.filePath.setText(msg)


class GraphDrawer(QWidget):
    def __init__(self):
        super().__init__()
        self.graph = None
        self.padding = 50
        self.points_to_labels = {}
        self.edges_to_weights = {}
        self.zoom = 1
        self.delta = QPoint(0, 0)
        self.start = self.delta
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

    def initLabels(self):
        for point in self.graph.points:
            self.points_to_labels[point.idx] = CustomLabel(str(point.idx), self)
            self.points_to_labels[point.idx].show()
        color = self.palette().color(self.backgroundRole()).name()
        for edge in self.graph.edges:
            self.edges_to_weights[edge.idx] = CustomLabel(str(edge.weight), self, color)
            self.edges_to_weights[edge.idx].show()

    def deleteLabels(self):
        for label in self.points_to_labels.values():
            label.setParent(None)
        for label in self.edges_to_weights.values():
            label.setParent(None)

    # TODO: add button to choose: show weights or not
    def setWeightLabelsVisible(self, flag):
        for label in self.edges_to_weights.values():
            label.setVisible(flag)
        self.update()

    def setGraph(self, graph):
        self.graph = graph
        self.deleteLabels()
        self.initLabels()
        self.update()

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
            d = min(int(self.padding * 1.5), int(self.graph.shortest_edge / 2 * min(map_x, map_y)))
            # choose suitable font size
            font_size = int(1 / self.graph.biggest_idx_len * d) * self.zoom
            # qlabel's font size must be greater than 0
            if font_size <= 0:
                font_size = 1

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
                lbl.setFontSize(font_size)
                lbl.move(
                    self.zoom * (x1 + (x2 - x1) // 2 + self.delta.x()) - lbl.width() // 2,
                    self.zoom * (y1 + (y2 - y1) // 2 + self.delta.y()) - lbl.height() // 2
                )

            painter.setBrush(QBrush(Qt.gray))
            painter.setPen(QPen(Qt.gray))

            for idx, (x, y) in pos.items():
                x = int(x * map_x) + self.padding
                y = int(y * map_y) + self.padding
                painter.drawEllipse(x - d // 2, y - d // 2, d, d)
                lbl = self.points_to_labels[idx]
                lbl.setFontSize(font_size)
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


class CustomLabel(QLabel):
    def __init__(self, text, parent, background_color=None):
        super().__init__(text, parent)
        if background_color:
            self.setStyleSheet(f"QLabel {{background-color: {background_color};}}")

    def setFontSize(self, font_size):
        font = self.font()
        font.setPointSize(font_size)
        self.setFont(font)
        self.resize(self.sizeHint())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Application()
    sys.exit(app.exec_())

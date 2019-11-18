import sys
import os
from PyQt5.QtWidgets import (QWidget, QApplication, QLabel, QScrollArea)
from PyQt5.QtGui import QPainter, QBrush, QPen, QFont, QTransform
from PyQt5.QtCore import Qt,QPoint
from helper import graph_from_json

# TODO, not save shortest edge.
class Application(QWidget):
    def __init__(self, graph):
        super().__init__()
        self.graph = graph
        self.padding = 50
        self.points_labels = {}
        self.max_node_radius = 50
        self.zoom=1
        self.delta=QPoint()
        self.delta.setX=0
        self.delta.setY=0
        self.start =self.delta
        self.mydelta=self.delta
        self.initLabels()
        self.initUI()
        self.pressing = False

    def initUI(self):
        #self.showMaximized()
        self.setGeometry(500, 500, self.width() // 2, self.height() // 2)
        self.setWindowTitle('Graph visualization')
        self.show()

    def initLabels(self):
        for idx in self.graph.pos: #TODO, change
            self.points_labels[idx] = QLabel(str(idx), self)
            self.points_labels[idx].show()

    def paintEvent(self, e):
        painter = QPainter()
        painter.begin(self)     
        x_coef = self.width() - 2 * self.padding
        y_coef = self.height() - 2 * self.padding
        pos = self.graph.pos        
        painter.scale(self.zoom,self.zoom)
        painter.translate(self.delta)
        self.delta.setX=self.start.x()
        self.delta.setY=self.start.y()   


        # maybe do property ?
        for edge in self.graph.edges.values():
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
            font.setPointSize(font_size)
            lbl.setFont(font)
            lbl.adjustSize()
            self.points_labels[idx].move(self.zoom*(x - lbl.width() // 2 + self.delta.x()), self.zoom*(y - lbl.height() // 2+self.delta.y()))
                  
        painter.end()


    def wheelEvent(self, event):
        self.zoom += event.angleDelta().y()/2880
        self.update()
        
    def mousePressEvent(self, QMouseEvent):
        #the pos of the widget when you first pressed it.
        self.start = QMouseEvent.pos()-self.delta
        self.beg_pos=[self.start.x(),self.start.y()]
        #to make sure you are holding mouse button down
        self.pressing = True

    def mouseMoveEvent(self, QMouseEvent):
        if self.pressing:
            self.end = QMouseEvent.pos()
            self.delta = (self.end-self.start)
            self.end = self.start
            self.update()

    def mouseReleaseEvent(self, QMouseEvent):
        self.pressing = False    


if __name__ == '__main__':
    if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
        print('You not specify file or such file doesn\'t exist')
        sys.exit(0)
    filename = sys.argv[1]


    app = QApplication(sys.argv)
    graph = graph_from_json(filename)
    win = Application(graph)
    win.resize(500,500)
    sys.exit(app.exec_())
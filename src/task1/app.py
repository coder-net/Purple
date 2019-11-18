import sys
import os
from PyQt5.QtWidgets import (QWidget, QApplication, QLabel, QScrollArea,QInputDialog,QFileDialog, QPushButton,QLineEdit,QGridLayout,QVBoxLayout )
    #QMainWindow, QDesktopWidget,   QAction
from PyQt5.QtGui import QPainter, QBrush, QPen, QFont
from PyQt5.QtCore import Qt,QPoint
from helper import graph_from_json

class Application(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()        

    def initUI(self):
        # Selecter input file
        file_label = QLabel("file", self)
        file_label.resize(file_label.sizeHint())
        file_label.move(20,5)
        file_label.setToolTip('end file ')
        self.filePath = QLineEdit("Select file", self)
        self.filePath.setObjectName("file")
        self.filePath.resize(self.filePath.sizeHint())
        self.filePath.move(120, 5)
        self.filePath.setToolTip('Select file')
        file_select_bytton = QPushButton('Select file', self)
        file_select_bytton.resize(file_select_bytton.sizeHint())
        file_select_bytton.move(300, 5)

        file_select_bytton.clicked.connect(lambda: self.selectFile()) 
        grid = QGridLayout()
        grid.addWidget(file_label,1,0)
        grid.addWidget(self.filePath,1,1)
        grid.addWidget(file_select_bytton,1,2)
        verticalLayout = QVBoxLayout()
        verticalLayout.setSpacing(0)
        graph_drawer = GraphDrawer()
        graph_drawer.resize(500,500)        
        self.graphWidget=graph_drawer  
        verticalLayout.addLayout(grid)
        verticalLayout.addWidget(self.graphWidget)
        self.setLayout(verticalLayout)
        self.show()


    def selectFile(self):
        self.filePath.setText(QFileDialog.getOpenFileName()[0])
        self.graphWidget.graph = graph_from_json(self.filePath.text())   
        if len(self.graphWidget.points_labels)>0:
            for idx in self.graphWidget.points_labels:    
                self.graphWidget.points_labels[idx].hide();
            self.graphWidget.points_labels.clear();
        self.graphWidget.initLabels()   

class GraphDrawer(QWidget):
    def __init__(self):
        super().__init__()
        self.graph = None
        self.padding = 100
        self.points_labels = {}
        self.max_node_radius = 50
        self.zoom=1
        self.delta=QPoint(0, 0)
        self.start =self.delta
        self.initUI()
        self.pressing = False

    def initUI(self):
        self.setGeometry(500, 500, self.width() // 2, self.height() // 2)
        self.setWindowTitle('Graph visualization')
        self.show()


    def initLabels(self):
        for idx in self.graph.points:
            self.points_labels[idx] = QLabel(str(idx), self)
            self.points_labels[idx].show()

    def paintEvent(self, e):
        if self.graph:
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
                font.setPointSize(font_size*self.zoom)
                lbl.setFont(font)
                lbl.adjustSize()
                self.points_labels[idx].move(self.zoom*(x -r/5 + self.delta.x()), self.zoom*(y-r/5+self.delta.y()))

            painter.end()        


    def wheelEvent(self, event):
        self.zoom += event.angleDelta().y()/2880
        self.update()

    def mousePressEvent(self, QMouseEvent):
        self.start = QMouseEvent.pos()-self.delta
        self.beg_pos=[self.start.x(),self.start.y()]
        self.pressing = True

    def mouseMoveEvent(self, QMouseEvent):
        if self.pressing:
            end = QMouseEvent.pos()
            self.delta = (end-self.start)
            self.update()

    def mouseReleaseEvent(self, QMouseEvent):
        self.pressing = False    


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win=Application()
    win.resize(600,800)
    sys.exit(app.exec_())

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys

# Simple drag and drop
# class Button(QPushButton):
  
#     def __init__(self, title, parent):
#         super().__init__(title, parent)
        
#         self.setAcceptDrops(True)
        

#     def dragEnterEvent(self, e):
      
#         if e.mimeData().hasFormat('text/plain'):
#             e.accept()
#         else:
#             e.ignore() 

#     def dropEvent(self, e):
        
#         self.setText(e.mimeData().text()) 


# class Example(QWidget):
  
#     def __init__(self):
#         super().__init__()
        
#         self.initUI()
        
        
#     def initUI(self):

#         edit = QLineEdit('', self)
#         edit.setDragEnabled(True)
#         edit.move(30, 65)

#         button = Button("Button", self)
#         button.move(190, 65)
        
#         self.setWindowTitle('Simple drag and drop')
#         self.setGeometry(300, 300, 300, 150)


## Button drag and drop
class Button(QPushButton):
  
    def __init__(self, title, parent):
        super().__init__(title, parent)
        

    def mouseMoveEvent(self, e):

        if e.buttons() != Qt.RightButton:
            return

        mimeData = QMimeData()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())

        dropAction = drag.exec_(Qt.MoveAction)


    def mousePressEvent(self, e):
      
        super().mousePressEvent(e)
        
        if e.button() == Qt.LeftButton:
            print('press')


class Example(QWidget):
  
    def __init__(self):
        super().__init__()

        self.initUI()
        
        
    def initUI(self):

        self.setAcceptDrops(True)

        self.button = Button('Button', self)
        self.button.move(100, 65)

        self.setWindowTitle('Click or Move')
        self.setGeometry(300, 300, 280, 150)
        

    def dragEnterEvent(self, e):
        e.accept()
        

    def dropEvent(self, e):

        position = e.pos()
        self.button.move(position)

        e.setDropAction(Qt.MoveAction)
        e.accept()


if __name__ == '__main__':
  
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    app.exec_()  
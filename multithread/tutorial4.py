## Tutorial 4 - Events and signals

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

## Signals and Slots
# class Example(QWidget):
    
#     def __init__(self):
#         super().__init__()
        
#         self.initUI()
        
        
#     def initUI(self):
        
#         lcd = QLCDNumber(self)
#         sld = QSlider(Qt.Horizontal, self)

#         vbox = QVBoxLayout()
#         vbox.addWidget(lcd)
#         vbox.addWidget(sld)

#         self.setLayout(vbox)
#         sld.valueChanged.connect(lcd.display)
        
#         self.setGeometry(300, 300, 250, 150)
#         self.setWindowTitle('Signal and slot')
#         self.show()

## Reimplementing event handler
# class Example(QWidget):
    
#     def __init__(self):
#         super().__init__()
        
#         self.initUI()
        
        
#     def initUI(self):      
        
#         self.setGeometry(300, 300, 250, 150)
#         self.setWindowTitle('Event handler')
#         self.show()
        
        
#     def keyPressEvent(self, e):
        
#         if e.key() == Qt.Key_Escape:
#             self.close()

## Event Object
# class Example(QWidget):
    
#     def __init__(self):
#         super().__init__()
        
#         self.initUI()
        
        
#     def initUI(self):      
        
#         grid = QGridLayout()
        
#         x = 0
#         y = 0
        
#         self.text = "x: {0},  y: {1}".format(x, y)
        
#         self.label = QLabel(self.text, self)
#         grid.addWidget(self.label, 0, 0, Qt.AlignTop)
        
#         self.setMouseTracking(True)
        
#         self.setLayout(grid)
        
#         self.setGeometry(300, 300, 350, 200)
#         self.setWindowTitle('Event object')
#         self.show()
        
        
#     def mouseMoveEvent(self, e):
        
#         x = e.x()
#         y = e.y()
        
#         text = "x: {0},  y: {1}".format(x, y)
#         self.label.setText(text)

## Event Sender
# class Example(QMainWindow):
    
#     def __init__(self):
#         super().__init__()
        
#         self.initUI()
        
        
#     def initUI(self):      

#         btn1 = QPushButton("Button 1", self)
#         btn1.move(30, 50)

#         btn2 = QPushButton("Button 2", self)
#         btn2.move(150, 50)
      
#         btn1.clicked.connect(self.buttonClicked)            
#         btn2.clicked.connect(self.buttonClicked)
        
#         self.statusBar()
        
#         self.setGeometry(300, 300, 290, 150)
#         self.setWindowTitle('Event sender')
#         self.show()
        
        
#     def buttonClicked(self):
      
#         sender = self.sender()
#         self.statusBar().showMessage(sender.text() + ' was pressed')

# ## Custom Signal
class Communicate(QObject):
    
    closeApp = pyqtSignal() 
    

class Example(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):      

        # self.c = Communicate()
        # self.c.closeApp.connect(self.close)       
        
        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('Emit signal')
        self.show()
        
        
    def mousePressEvent(self, event):
        self.close()
        # self.c.closeApp.emit()

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
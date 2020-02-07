from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys

## QPixMap
# class Example(QWidget):
    
#     def __init__(self):
#         super().__init__()
        
#         self.initUI()
        
        
#     def initUI(self):      

#         hbox = QHBoxLayout(self)
#         pixmap = QPixmap("./panda.jpg") #png not work

#         lbl = QLabel(self)
#         lbl.setPixmap(pixmap)

#         hbox.addWidget(lbl)
#         self.setLayout(hbox)
        
#         self.move(300, 200)
#         self.setWindowTitle('Red Rock')
#         self.show()        

## QLineEdit
# class Example(QWidget):
    
#     def __init__(self):
#         super().__init__()
        
#         self.initUI()
        
        
#     def initUI(self):      

#         self.lbl = QLabel(self)
#         qle = QLineEdit(self)
        
#         qle.move(60, 100)
#         self.lbl.move(60, 40)

#         qle.textChanged[str].connect(self.onChange)
        
#         self.setGeometry(300, 300, 280, 170)
#         self.setWindowTitle('QLineEdit')
#         self.show()
        
#     def onChange(self, text):
#         self.lbl.setText(text)
#         self.lbl.adjustSize()   

## QSplitter    
# class Example(QWidget):
    
#     def __init__(self):
#         super().__init__()
        
#         self.initUI()
        
        
#     def initUI(self):      

#         hbox = QHBoxLayout(self)

#         # pixmap = QPixmap("./panda.jpg")
#         topleft = QFrame(self)
#         topleft.setFrameShape(QFrame.StyledPanel)
#         # topleft.setPixmap(pixmap)

#         topright = QFrame(self)
#         topright.setFrameShape(QFrame.StyledPanel)

#         bottom = QFrame(self)
#         bottom.setFrameShape(QFrame.StyledPanel)

#         splitter1 = QSplitter(Qt.Horizontal)
#         splitter1.addWidget(topleft)
#         splitter1.addWidget(topright)

#         splitter2 = QSplitter(Qt.Vertical)
#         splitter2.addWidget(splitter1)
#         splitter2.addWidget(bottom)

#         hbox.addWidget(splitter2)
#         self.setLayout(hbox)
        
#         self.setGeometry(300, 300, 300, 200)
#         self.setWindowTitle('QSplitter')
#         self.show()

## QComboBox
class Example(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):      

        self.lbl = QLabel("Ubuntu", self)

        combo = QComboBox(self)
        combo.addItem("Ubuntu")
        combo.addItem("Mandriva")
        combo.addItem("Fedora")
        combo.addItem("Arch")
        combo.addItem("Gentoo")

        combo.move(50, 50)
        self.lbl.move(50, 150)

        combo.activated[str].connect(self.onActivated)        
         
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('QComboBox')
        self.statusBar().showMessage("Ready")
        
        self.show()
        
        
    def onActivated(self, text):
      
        self.lbl.setText(text)
        self.lbl.adjustSize()  

        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
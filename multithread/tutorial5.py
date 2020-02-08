## Tutorial 5 - Dialogs

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

## Dialog
# class Example(QWidget):
    
#     def __init__(self):
#         super().__init__()
        
#         self.initUI()
        
        
#     def initUI(self):      

#         self.btn = QPushButton('Dialog', self)
#         self.btn.move(20, 20)
#         self.btn.clicked.connect(self.showDialog)
        
#         self.le = QLineEdit(self)
#         self.le.move(130, 22)
        
#         self.setGeometry(300, 300, 290, 150)
#         self.setWindowTitle('Input dialog')
#         self.show()
        
        
#     def showDialog(self):
        
#         text, ok = QInputDialog.getText(self, 'Input Dialog', 
#             'Enter your name:')
        
#         if ok:
#             self.le.setText(str(text))
#         if not ok:
#             self.le.setText("Cancel")

# Color Dialog
class Example(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):      

        col = QColor(0, 0, 0) 

        self.btn = QPushButton('Dialog', self)
        self.btn.move(20, 20)

        self.btn.clicked.connect(self.showDialog)

        self.frm = QFrame(self)
        self.frm.setStyleSheet("QWidget { background-color: %s }" 
            % col.name())
        self.frm.setGeometry(130, 22, 100, 100)            
        
        self.setGeometry(300, 300, 250, 180)
        self.setWindowTitle('Color dialog')
        self.show()
        
        
    def showDialog(self):
        col = QColorDialog.getColor()

        if col.isValid():
            self.frm.setStyleSheet("QWidget { background-color: %s }"
                % col.name())

## Font Dialog
# class Example(QWidget):
    
#     def __init__(self):
#         super().__init__()
        
#         self.initUI()
        
        
#     def initUI(self):      

#         vbox = QVBoxLayout()

#         btn = QPushButton('Dialog', self)
#         btn.setSizePolicy(QSizePolicy.Fixed,
#             QSizePolicy.Fixed)
        
#         btn.move(20, 20)

#         vbox.addWidget(btn)

#         btn.clicked.connect(self.showDialog)
        
#         self.lbl = QLabel('Knowledge only matters', self)
#         self.lbl.move(130, 20)

#         vbox.addWidget(self.lbl)
#         self.setLayout(vbox)          
        
#         self.setGeometry(300, 300, 250, 180)
#         self.setWindowTitle('Font dialog')
#         self.show()
        
        
#     def showDialog(self):

#         font, ok = QFontDialog.getFont()
#         if ok:
#             self.lbl.setFont(font)

# ## QFile Dialog
# class Example(QMainWindow):
    
#     def __init__(self):
#         super().__init__()
        
#         self.initUI()
        
        
#     def initUI(self):      

#         self.textEdit = QTextEdit()
#         self.setCentralWidget(self.textEdit)
#         self.statusBar()

#         openFile = QAction(QIcon('open.png'), 'Open', self)
#         openFile.setShortcut('Ctrl+O')
#         openFile.setStatusTip('Open new File')
#         openFile.triggered.connect(self.showDialog)

#         menubar = self.menuBar()
#         fileMenu = menubar.addMenu('&File')
#         fileMenu.addAction(openFile)       
        
#         self.setGeometry(300, 300, 350, 300)
#         self.setWindowTitle('File dialog')
#         self.show()
        
        
#     def showDialog(self, s):
#         pass
        # fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')

        # if fname[0]:
            # f = open(fname[0], 'r')

            # with f:
                # data = f.read()
                # self.textEdit.setText(data)


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
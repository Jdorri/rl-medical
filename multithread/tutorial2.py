import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

## Status bar
# class Example(QMainWindow):
    
#     def __init__(self):
#         super().__init__()
        
#         self.initUI()
        
#     def initUI(self):               
        
#         self.statusBar().showMessage('Ready')
        
#         self.setGeometry(300, 300, 250, 150)
#         self.setWindowTitle('Statusbar')    
#         self.show()

## Menu bar (Menu & Sub-Menu)
# class Example(QMainWindow):
    
#     def __init__(self):
#         super().__init__()
        
#         self.initUI()
        
        
#     def initUI(self):               
#         menubar = self.menuBar()

#         # Exit action
#         exitAct = QAction(QIcon('exit.png'), '&Exit', self)        
#         exitAct.setShortcut('Ctrl+Q')
#         exitAct.setStatusTip('Exit application')
#         exitAct.triggered.connect(qApp.quit)

#         # New action
#         newAct = QAction("New", self)

#         # Import action
#         impAct = QAction("Import main", self)

#         # Primary menu
#         fileMenu = menubar.addMenu('&File') # & gives _ to first char
#         fileMenu.addAction(exitAct)

#         editMenu = menubar.addMenu('&Edit')
#         editMenu.addAction(exitAct)

#         # Sub menu
#         impMenu = QMenu("Import", self)
#         impMenu.addAction(impAct)

#         fileMenu.addAction(newAct)
#         fileMenu.addMenu(impMenu)
        
#         # Window styling
#         self.setGeometry(300, 300, 1300, 800)
#         self.setWindowTitle('Simple menu')    
#         self.show()

## Checked Menu
# class Example(QMainWindow):
    
#     def __init__(self):
#         super().__init__()
        
#         self.initUI()    
        
#     def initUI(self):         
#         self.statusbar = self.statusBar()
#         self.statusbar.showMessage('Ready')
        
#         menubar = self.menuBar()
#         viewMenu = menubar.addMenu('View')
        
#         viewStatAct = QAction('View statusbar', self, checkable=True)
#         viewStatAct.setStatusTip('View statusbar')
#         viewStatAct.setChecked(True)
#         viewStatAct.triggered.connect(self.toggleMenu)
        
#         viewMenu.addAction(viewStatAct)
        
#         self.setGeometry(300, 300, 300, 200)
#         self.setWindowTitle('Check menu')    
#         self.show()
        
#     def toggleMenu(self, state):
#         if state:
#             self.statusbar.show()
#         else:
#             self.statusbar.hide()

## Context Menu
# class Example(QMainWindow):
    
#     def __init__(self):
#         super().__init__()
        
#         self.initUI()
        
        
#     def initUI(self):         
        
#         self.setGeometry(300, 300, 300, 200)
#         self.setWindowTitle('Context menu')    
#         self.show()
    
    
#     def contextMenuEvent(self, event):
       
#            cmenu = QMenu(self)
           
#            newAct = cmenu.addAction("New")
#            opnAct = cmenu.addAction("Open")
#            quitAct = cmenu.addAction("Quit")
#            action = cmenu.exec_(self.mapToGlobal(event.pos()))
           
#            if action == quitAct:
#                qApp.quit()

## Putting it together
class Example(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
    def initUI(self):               
        textEdit = QTextEdit()
        self.setCentralWidget(textEdit) # occupy all space that is left

        exitAct = QAction(QIcon('exit24.png'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)

        self.statusBar().showMessage("Ready")

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAct)
        
        self.setGeometry(300, 300, 1300, 800)
        self.setWindowTitle('Main window')    
        self.show()

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QPushButton, QMessageBox, QDesktopWidget
from PyQt5.QtGui import QIcon, QFont

## Procedural Style
# if __name__ == '__main__':
#     # Create an application object
#     app = QApplication(sys.argv)

#     # QWidget widget is base class of all user interface objects
#     w = QWidget()
#     w.resize(250, 150) # 250px wide and 150px height
#     w.move(300, 300) # move to position x=300, y=300 on the screen
#     w.setWindowTitle('Simple')
#     w.show()
    
#     sys.exit(app.exec_()) # ensure clean exit, run the code

# ## Object Oriented Style
# class Example(QWidget):
#     def __init__(self):
#         super().__init__()

#         self.initUI()
    
#     def initUI(self):
#         QToolTip.setFont(QFont('SansSerif', 10))
        
#         # # Create a tool tip
#         # self.setToolTip('This is a <b>QWidget</b> widget')
        
#         # # Create a push button
#         # btn = QPushButton('Button', self)
#         # btn.setToolTip('This is a <b>QPushButton</b> widget')
#         # btn.resize(btn.sizeHint())
#         # btn.move(50, 50) 

#         qbtn = QPushButton('Quit', self)
#         qbtn.clicked.connect(QApplication.instance().quit)
#         qbtn.resize(qbtn.sizeHint())
#         qbtn.move(50, 50)   

#         # (x, y, width, height)
#         self.setGeometry(300, 300, 300, 220)
#         self.setWindowTitle("icon")
#         self.setWindowIcon(QIcon("web.png"))

#         self.show()

## Quit with Message
class Example(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):               
        
        self.resize(400, 150)
        self.center()       
        self.setWindowTitle('Message box')    
        self.show()
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    # Override to modify widget behaviour when closing 
    def closeEvent(self, event):
        
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()  

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import time

class MyThread(QThread):
    change_value = pyqtSignal(int)

    def run(self):
        count = 0
        while count < 100:
            count += 1

            time.sleep(0.3)
            self.change_value.emit(count)

class Window(QDialog):

    def __init__(self):
        super().__init__()

        self.title = "PyQt 5 Window"
        self.left = 500
        self.top = 200
        self.width = 300
        self.height = 100

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.initUI()
        
        self.show()

    def initUI(self):
        vbox = QVBoxLayout()
        self.progressbar = QProgressBar()
        self.progressbar.setMaximum(100)
        vbox.addWidget(self.progressbar)

        self.button = QPushButton("Run Progressbar")
        self.button.clicked.connect(self.startProgressVar)
        self.button.setStyleSheet("background-color:yellow")
        vbox.addWidget(self.button)

        self.setLayout(vbox)
    
    def startProgressVar(self):
        self.thread = MyThread()
        self.thread.change_value.connect(self.setProgressVal)

        self.thread.start()

    def setProgressVal(self, val):
        self.progressbar.setValue(val)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = Window()
    sys.exit(app.exec_())


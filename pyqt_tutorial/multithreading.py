from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import time

<<<<<<< HEAD
def hello_world():
    print("hello world")

class MyThread(QThread):
    change_value = pyqtSignal(int)
    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        self.func()
=======
class MyThread(QThread):
    change_value = pyqtSignal(int)

    def run(self):
>>>>>>> UI_for_running_algorithm_and_option_selection
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
<<<<<<< HEAD
        self.thread = None
=======
>>>>>>> UI_for_running_algorithm_and_option_selection

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
        print(viewer.thread)
        self.thread = MyThread(hello_world)
        self.thread.change_value.connect(self.setProgressVal)

        self.thread.start()

    def setProgressVal(self, val):
        self.progressbar.setValue(val)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = Window()
    viewer.thread = "haha"
    print(viewer.thread)
    sys.exit(app.exec_())


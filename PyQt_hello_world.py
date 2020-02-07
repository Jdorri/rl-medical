import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):



app = QApplication(sys.argv)

window = QMainWindow()
window.show()

app.exec_()

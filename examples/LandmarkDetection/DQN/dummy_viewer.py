from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import numpy as np

class BasicViewer(QWidget):
    signal = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        
        self.initUI()

        self.setGeometry(300, 300, 1350, 800)
        self.setWindowTitle('Dummy GUI')

        self.signal.connect(self.signal_handler)    
        self.show()
        
        
    def initUI(self):
        
        self.title = QLabel('Title')
        self.author = QLabel('Author')
        self.label = QLabel('Review')

        titleEdit = QLineEdit()
        authorEdit = QLineEdit()
        reviewEdit = QTextEdit()

        grid = QGridLayout()
        grid.setSpacing(10) # Vertical spacing

        grid.addWidget(self.title, 1, 0)
        grid.addWidget(titleEdit, 1, 1)

        grid.addWidget(self.author, 2, 0)
        grid.addWidget(authorEdit, 2, 1)

        grid.addWidget(self.label, 3, 0)
        # Span 5 rows and 1 column
        grid.addWidget(reviewEdit, 3, 1, 50, 1)
        
        self.setLayout(grid) 
    
    ## SIGNAL HANDLER
    @pyqtSlot(dict)
    def signal_handler(self, value):
        print("receive signal")
        # self.draw_image(
        #     app=value["app"],
        #     arrs=value["arrs"],
        #     agent_loc=value["agent_loc"],
        #     target=value["target"],
        #     text=value["text"],
        #     spacing=value["spacing"],
        #     rect=value["rect"]
        # )
        self.label.setText(str(value["agent_loc"]))
        # self.label.setStyleSheet("QLabel {background-color: white }")
        print(value)
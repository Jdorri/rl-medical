## Tutorial 3 - Layout Management

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys

## Absolute Positioning
# class Example(QWidget):
    
#     def __init__(self):
#         super().__init__()
        
#         self.initUI()
        
        
#     def initUI(self):
        
#         lbl1 = QLabel('Maleakhi', self)
#         lbl1.move(15, 10) # (x, y) starting position top-left

#         lbl2 = QLabel('Agung', self)
#         lbl2.move(35, 40)
        
#         lbl3 = QLabel('Wijaya', self)
#         lbl3.move(55, 70)        
        
#         self.setGeometry(300, 300, 250, 150)
#         self.setWindowTitle('Absolute')    
#         self.show()

## Horizontal and Vertical Box
# class Example(QWidget):
    
#     def __init__(self):
#         super().__init__()
        
#         self.initUI()
        
        
#     def initUI(self):
        
#         okButton = QPushButton("OK")
#         cancelButton = QPushButton("Cancel")

#         hbox = QHBoxLayout()
#         hbox.addStretch(1)
#         hbox.addWidget(okButton)
#         hbox.addWidget(cancelButton)
#         # Stretch push button to the right

#         vbox = QVBoxLayout()
#         vbox.addStretch(1)
#         vbox.addLayout(hbox)
#         # Stretch push button to the bottom
        
#         self.setLayout(vbox)    
        
#         self.setGeometry(300, 300, 300, 150)
#         self.setWindowTitle('Buttons')    
#         self.show()

## Grid Layout
# class Example(QWidget):
    
#     def __init__(self):
#         super().__init__()
        
#         self.initUI()
        
        
#     def initUI(self):
        
#         grid = QGridLayout()
#         self.setLayout(grid)
 
#         names = ['Cls', 'Bck', '', 'Close',
#                  '7', '8', '9', '/',
#                 '4', '5', '6', '*',
#                  '1', '2', '3', '-',
#                 '0', '.', '=', '+']
        
#         positions = [(i,j) for i in range(5) for j in range(4)]
        
#         for position, name in zip(positions, names):
            
#             if name == '':
#                 continue
#             button = QPushButton(name)
#             grid.addWidget(button, *position)
            
#         self.move(300, 150)
#         self.setWindowTitle('Calculator')
#         self.show()

class Example(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):
        
        title = QLabel('Title')
        author = QLabel('Author')
        review = QLabel('Review')

        titleEdit = QLineEdit()
        authorEdit = QLineEdit()
        reviewEdit = QTextEdit()

        grid = QGridLayout()
        grid.setSpacing(10) # Vertical spacing

        grid.addWidget(title, 1, 0)
        grid.addWidget(titleEdit, 1, 1)

        grid.addWidget(author, 2, 0)
        grid.addWidget(authorEdit, 2, 1)

        grid.addWidget(review, 3, 0)
        # Span 5 rows and 1 column
        grid.addWidget(reviewEdit, 3, 1, 50, 1)
        
        self.setLayout(grid) 
        
        self.setGeometry(300, 300, 1350, 800)
        self.setWindowTitle('Review')    
        self.show()
        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
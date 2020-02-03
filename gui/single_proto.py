import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QPushButton
from PyQt5.QtGui import QPixmap, QPainter,QColor, QFont, QImage, QIcon
from PyQt5 import QtGui, QtCore
import PyQt5 as Qt
import cv2

class App(QWidget):

    def __init__(self, rect_centre, target, spacing, error, depth):
        super().__init__()
        self.title = 'PyQt5 image - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480

        # Set location and dimensions of overlay rectangle
        self.rect_w = 75 * spacing
        self.rect_h = 75 * spacing
        self.rect_x, self.rect_y = rect_centre

        self.initUI()

        # cvImg = np.random.randint(255, size=(200,200,3),dtype=np.uint8)
        arr = cv2.imread('images/test.png')
        cvImg = arr
        height, width, channel = cvImg.shape
        bytesPerLine = 3 * width
        qImg = QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888)

        # image
        self.im = QPixmap(qImg)
        self.label = QLabel()

        # create painter instance with pixmap
        self.painterInstance = QPainter(self.im)

        self.draw_rects(error, spacing)
        self.draw_circles(rect_centre, target, depth)

        # put images on labels
        self.label.setPixmap(self.im)
        # self.label2 = QLabel()
        # self.label2.setPixmap(self.im)
        # self.label3 = QLabel()
        # self.label3.setPixmap(self.im)

        self.grid = QGridLayout()
        self.grid.addWidget(self.label,1,2)
        # self.grid.addWidget(self.label2,1,3)
        # self.grid.addWidget(self.label3,2,2)
        self.grid.addWidget(QPushButton('Up'),1,1)
        self.grid.addWidget(QPushButton('Down'),2,1)

        x = y = 0
        self.text = "x: {0},  y: {1}".format(x, y)
        self.label4 = QLabel(self.text, self)
        self.grid.addWidget(self.label4, 0, 2)
        # self.im.mousePressEvent = self.getPos

        self.setLayout(self.grid)

        self.setGeometry(10,10,320,300)
        self.setWindowTitle("PyQT show image")
        self.label.QPixmap.fromImage(im)
        self.show()
        self.painterInstance.end()

        self.show()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create widget
        label = QLabel(self)
        pixmap = QPixmap('images/test.png')
        label.setPixmap(pixmap)
        self.resize(pixmap.width(),pixmap.height())

        self.setMouseTracking(True)

    def mouseMoveEvent(self, e):
        '''Stops tracking when the mouse moves over the image. Need to fix.'''
        x = e.x()
        y = e.y()
        text = "x: {0},  y: {1}".format(x, y)
        self.label4.setText(text)

    def draw_circles(self, centre, target, depth):
        # draw circle at current agent location
        self.penCentre = QtGui.QPen(QtCore.Qt.blue)
        self.penCentre.setWidth(3)
        self.painterInstance.setPen(self.penCentre)
        centre = QtCore.QPoint(self.rect_x, self.rect_y)
        self.painterInstance.drawEllipse(centre, 2, 2)

        # draw circle at target location
        self.penCentre = QtGui.QPen(QtCore.Qt.red)
        self.penCentre.setWidth(3)
        self.painterInstance.setPen(self.penCentre)
        centre = QtCore.QPoint(*target)
        self.painterInstance.drawEllipse(centre, 2, 2)

        # draw circle surrounding target
        self.penCirlce = QtGui.QPen(QColor(255,0,0,0))
        self.penCirlce.setWidth(3)
        self.painterInstance.setPen(self.penCirlce)
        self.painterInstance.setBrush(QtCore.Qt.red)
        self.painterInstance.setOpacity(0.2)
        centre = QtCore.QPoint(*target)
        radx = rady = depth * 30
        self.painterInstance.drawEllipse(centre, radx, rady)

    def draw_rects(self, error, spacing):
        # Coordinates for overlayed rectangle
        xPos = self.rect_x - self.rect_w//2
        yPos = self.rect_y - self.rect_h//2
        xLen = self.rect_w
        yLen = self.rect_h

        # set rectangle color and thickness
        self.penRectangle = QtGui.QPen(QtCore.Qt.cyan)
        self.penRectangle.setWidth(3)
        # draw rectangle on painter
        self.painterInstance.setPen(self.penRectangle)
        self.painterInstance.drawRect(xPos,yPos,xLen,yLen)

        # Annotate rectangle
        self.painterInstance.setPen(QtCore.Qt.cyan)
        self.painterInstance.setFont(QFont('Decorative', yLen//5))
        self.painterInstance.drawText(xPos, yPos-8, "Agent")
        # Add error message
        self.painterInstance.setPen(QtCore.Qt.darkGreen)
        self.painterInstance.setFont(QFont('Decorative', self.height//15))
        self.painterInstance.drawText(self.width//10, self.height*17//20, f"Error {error}mm")
        # Add spacing message
        self.painterInstance.setPen(QtCore.Qt.darkGreen)
        self.painterInstance.setFont(QFont('Decorative', self.height//15))
        self.painterInstance.drawText(self.width*1//2, self.height*17//20, f'Spacing {spacing}')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App(rect_centre=(150, 200), target=(300,300), spacing=2, error='2.34', depth=3)
    sys.exit(app.exec_())

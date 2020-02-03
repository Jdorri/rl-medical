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

        self.image = QImage('images/test.png')
        self.image = QLabel()
        # self.image.setPixmap(QPixmap("C:\\myImg.jpg"))
        self.image.setObjectName("image")
        self.image.mousePressEvent = self.getPos

        def getPos(self , event):
            x = event.pos().x()
            y = event.pos().y()
        # pixmap = QPixmap(QPixmap.fromImage(self.img))
        # img_label = QLabel()
        # img_label.setPixmap(pixmap)
        # img_label.mousePressEvent = self.getPixel
        #
        # def getPixel(self, event):
        #     x = event.pos().x()
        #     y = event.pos().y()
        #     c = self.img.pixel(x,y)  # color code (integer): 3235912
        #     # depending on what kind of value you like (arbitary examples)
        #     c_qobj = QColor(c)  # color object
        #     c_rgb = QColor(c).getRgb()  # 8bit RGBA: (255, 23, 0, 255)
        #     c_rgbf = QColor(c).getRgbf()  # RGBA float: (1.0, 0.3123, 0.0, 1.0)
        #     return x, y, c_rgb


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App(rect_centre=(150, 200), target=(300,300), spacing=2, error='2.34', depth=3)
    sys.exit(app.exec_())

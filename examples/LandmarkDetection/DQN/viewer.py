import os
import math
import io
from PIL import Image, ImageTk
import tkinter as tk
import cv2
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys

try:
    import pyglet
    from pyglet.gl import *
except ImportError as e:
    reraise(suffix="HINT: you can install pyglet directly via 'pip install pyglet'. But if you really just want to install all Gym dependencies and not have to think about it, 'pip install -e .[all]' or 'pip install gym[all]' will do it.")

class SimpleImageViewer(QWidget):
    ''' Simple image viewer class for rendering images using pyglet'''
    agent_signal = pyqtSignal(dict)

    def __init__(self, arr, arr_x, arr_y, scale_x=1, scale_y=1, filepath=None, display=None):

        super().__init__()

        self.isopen = False
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.display = display
        self.filepath = filepath
        self.filename = os.path.basename(filepath)

        # Set image formatting and get shape
        cvImg = arr.astype(np.uint8)
        self.height, self.width, self.channel = cvImg.shape
        cvImg_x = arr_x.astype(np.uint8)
        self.height_x, self.width_x, self.channel_x = cvImg_x.shape
        cvImg_y = arr_y.astype(np.uint8)
        self.height_y, self.width_y, self.channel_y = cvImg_y.shape

        # initialize window with the input image
        assert arr.shape == (self.height, self.width, 3), "You passed in an image with the wrong number shape"
        
        ########################################################################
        ## PyQt GUI Code Section

        # Convert image to correct format
        bytesPerLine = 3 * self.width
        qImg = QImage(cvImg.data, self.width, self.height, bytesPerLine, QImage.Format_RGB888)
        bytesPerLine = 3 * self.width_x
        qImg_x = QImage(cvImg_x.data, self.width_x, self.height_x, bytesPerLine, QImage.Format_RGB888)
        bytesPerLine = 3 * self.width_y
        qImg_y = QImage(cvImg_y.data, self.width_y, self.height_y, bytesPerLine, QImage.Format_RGB888)

        # Initialise images with labels
        self.im = QPixmap(qImg)
        self.im_x = QPixmap(qImg_x)
        self.im_y = QPixmap(qImg_y)
        self.label = QLabel()
        # self.label.setPixmap(self.im)
        self.label2 = QLabel()
        self.label2.setPixmap(self.im_x)
        self.label3 = QLabel()
        self.label3.setPixmap(self.im_y)

        # Set background color for images to Black
        self.label.setAutoFillBackground(True)
        self.label2.setAutoFillBackground(True)
        self.label3.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.label.setPalette(p)
        self.label2.setPalette(p)
        self.label3.setPalette(p)

        # Initiliase Grid
        self.grid = QGridLayout()
        self.grid.addWidget(self.label,1,2)
        self.grid.addWidget(self.label2,1,3)
        self.grid.addWidget(self.label3,2,2)
        self.button_up = QPushButton("Up")
        self.grid.addWidget(self.button_up,1,1)
        self.grid.addWidget(QPushButton('Down'),2,1)
        self.agent_signal.connect(self.agent_signal_handler)

        # Set Layout of GUI
        self.setLayout(self.grid)
        self.setGeometry(10,10,320,200)

        self.setWindowTitle("Landmark Detection Agent")
        self.show()

        ########################################################################

    ########################################################################
    ## PyQt GUI Code Section

    def draw_image(self, arrs, agent_loc, target=(200,200), depth=1, text=None, spacing=1, rect=None):
        """
        Main image drawer function
        """
        # Draw background image (brain)
        cvImg = arrs[0].astype(np.uint8)
        self.height, self.width, self.channel = cvImg.shape
        bytesPerLine = 3 * self.width
        qImg = QImage(cvImg.data, self.width, self.height, bytesPerLine, QImage.Format_RGB888)
        self.img = QPixmap(qImg) # can use this to scale the image: .scaled(450, 350, QtCore.Qt.KeepAspectRatio)

        cvImg_x = arrs[1].astype(np.uint8)
        self.height_x, self.width_x, self.channel_x = cvImg_x.shape
        bytesPerLine = 3 * self.width_x
        qImg_x = QImage(cvImg_x.data, self.width_x, self.height_x, bytesPerLine, QImage.Format_RGB888)
        self.img_x = QPixmap(qImg_x)

        cvImg_y = arrs[2].astype(np.uint8)
        self.height_y, self.width_y, self.channel_y = cvImg_y.shape
        bytesPerLine = 3 * self.width_y
        qImg_y = QImage(cvImg_y.data, self.width_y, self.height_y, bytesPerLine, QImage.Format_RGB888)
        self.img_y = QPixmap(qImg_y)

        # Draw some rectangle and agent (overlay)
        self.painterInstance = QPainter(self.img)
        _agent_loc = (agent_loc[1], agent_loc[0])
        self.draw_rects(text, spacing, _agent_loc, rect[:4])
        self.draw_circles(_agent_loc, target, depth)
        self.painterInstance.end()

        self.painterInstance = QPainter(self.img_x)
        _agent_loc = (agent_loc[2], agent_loc[1])
        self.draw_rects(text, spacing, _agent_loc, rect[2:])
        self.draw_circles(_agent_loc, target, depth)
        self.painterInstance.end()

        self.painterInstance = QPainter(self.img_y)
        _agent_loc = (agent_loc[0], self.height_y-agent_loc[2])       # Rotate 90 degrees ccw
        rect = (self.height_y-rect[4], self.height_y-rect[5]) + rect[:2]
        self.draw_rects(text, spacing, agent_loc, rect)
        self.draw_circles(_agent_loc, target, depth)
        self.painterInstance.end()

        self.label.setPixmap(self.img)
        self.label2.setPixmap(self.img_x)
        self.label3.setPixmap(self.img_y)

        self.show()

    def draw_circles(self, agent_loc, target, depth):
        # Draw current agent location
        self.penCentre = QPen(Qt.blue)
        self.penCentre.setWidth(3)
        self.painterInstance.setPen(self.penCentre)
        centre = QPoint(*agent_loc)
        self.painterInstance.drawEllipse(centre, 2, 2)

        # Draw circle at target location
        if target is not None:
            self.penCentre = QPen(Qt.red)
            self.penCentre.setWidth(3)
            self.painterInstance.setPen(self.penCentre)
            centre = QPoint(*target)
            self.painterInstance.drawEllipse(centre, 2, 2)

            # draw circle surrounding target
            self.penCirlce = QPen(QColor(255,0,0,0))
            self.penCirlce.setWidth(3)
            self.painterInstance.setPen(self.penCirlce)
            self.painterInstance.setBrush(Qt.red)
            self.painterInstance.setOpacity(0.2)
            centre = QPoint(*target)
            radx = rady = depth * 30
            self.painterInstance.drawEllipse(centre, radx, rady)

    def draw_rects(self, text, spacing, agent_loc, rect):
        # Coordinates for overlayed rectangle (ROI)
        xPos = rect[2]
        yPos = rect[0]
        xLen = rect[3] - xPos
        yLen = rect[1] - yPos

        # set rectangle color and thickness
        self.penRectangle = QPen(Qt.cyan)
        self.penRectangle.setWidth(3)
        # draw rectangle on painter
        self.painterInstance.setPen(self.penRectangle)
        self.painterInstance.drawRect(xPos,yPos,xLen,yLen)

        # Annotate rectangle
        self.painterInstance.setPen(Qt.cyan)
        self.painterInstance.setFont(QFont('Decorative', min(abs(yLen)//12, 15)))
        self.painterInstance.drawText(xPos, yPos-8, "Agent")

    @pyqtSlot(dict)
    def agent_signal_handler(self, value):
        """
        Used to handle agent signal when it moves.
        """
        self.draw_image(
            arrs=value["arrs"],
            agent_loc=value["agent_loc"],
            target=value["target"],
            text=value["text"],
            spacing=value["spacing"],
            rect=value["rect"]
        )

    ########################################################################
    
    def render(self):
        self.window.flip()

    def saveGif(self,filename=None,arr=None,duration=0):
        arr[0].save(filename, save_all=True,
                    append_images=arr[1:],
                    duration=500,
                    quality=95) # duration milliseconds

    def close(self):
        if self.isopen:
            self.window.close()
            self.isopen = False

    def __del__(self):
        self.close()

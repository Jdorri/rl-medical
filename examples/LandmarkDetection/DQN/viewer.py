
import os
import math
import io
# import PySimpleGUI as sg
from PIL import Image, ImageTk
import tkinter as tk
import cv2
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtGui, QtCore
import sys


try:
    import pyglet
    from pyglet.gl import *
except ImportError as e:
    reraise(suffix="HINT: you can install pyglet directly via 'pip install pyglet'. But if you really just want to install all Gym dependencies and not have to think about it, 'pip install -e .[all]' or 'pip install gym[all]' will do it.")

class SimpleImageViewer(QWidget):
    ''' Simple image viewer class for rendering images using pyglet'''

    def __init__(self, app, arr, arr_x, arr_y, scale_x=1, scale_y=1, filepath=None, display=None):

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
        self.label.setPixmap(self.im)
        self.label2 = QLabel()
        self.label2.setPixmap(self.im_x)
        self.label3 = QLabel()
        self.label3.setPixmap(self.im_y)

        # Set background color for images to Black
        self.label.setAutoFillBackground(True)
        self.label2.setAutoFillBackground(True)
        self.label3.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.black)
        self.label.setPalette(p)
        self.label2.setPalette(p)
        self.label3.setPalette(p)

        # Initiliase Grid
        self.grid = QGridLayout()
        self.grid.addWidget(self.label,1,2)
        self.grid.addWidget(self.label2,1,3)
        self.grid.addWidget(self.label3,2,2)
        self.grid.addWidget(QPushButton('Up'),1,1)
        self.grid.addWidget(QPushButton('Down'),2,1)

        # Set Layout of GUI
        self.setLayout(self.grid)
        self.setGeometry(10,10,320,200)

        self.setWindowTitle("Landmark Detection Agent")
        self.show()

        # self.window = pyglet.window.Window(width=scale_x*width,
        #                                    height=scale_y*height,
        #                                    caption=self.filename,
        #                                    display=self.display,
        #                                    resizable=True,
        #                                    # fullscreen=True # ruins screen resolution
        #                                    )
        ## set location
        # screen_width = self.window.display.get_default_screen().width
        # screen_height = self.window.display.get_default_screen().height
        # self.location_x = screen_width / 2 - 2*width
        # self.location_y = screen_height / 2 - 2*height
        # self.location_x = screen_width / 2 - width
        # self.location_y = screen_height / 2 - height
        # self.window.set_location((int)(self.location_x), (int)(self.location_y))

        # ## scale window size
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        # glScalef(scale_x, scale_y, 1.0)

        # self.img_width = width
        # self.img_height = height
        # self.isopen = True

        # self.window_width, self.window_height = self.window.get_size()

        # # turn on transparency
        # glEnable(GL_BLEND)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


    def draw_image(self, app, arrs, agent_loc, target=(200,200), depth=1, text=None, spacing=1, rect=None):
        # convert data typoe to GLubyte
        # rawData = (GLubyte * arr.size)(*list(arr.ravel().astype('int')))
        # # image = pyglet.image.ImageData(self.img_width, self.img_height, 'RGB',
        # #                                rawData, #arr.tostring(),
        # #                                pitch=self.img_width * -3)
        # self.window.clear()
        # self.window.switch_to()
        # self.window.dispatch_events()
        # image.blit(0,0)

        # Convert image to format
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
        # _agent_loc = (agent_loc[2], agent_loc[0])       # Rotate 90 degrees ccw
        # rect = rect[:2] + rect[4:]
        rect = (self.height_y-rect[4], self.height_y-rect[5]) + rect[:2]
        self.draw_rects(text, spacing, agent_loc, rect)
        self.draw_circles(_agent_loc, target, depth)
        self.painterInstance.end()

        self.label.setPixmap(self.img)
        self.label2.setPixmap(self.img_x)
        self.label3.setPixmap(self.img_y)

        self.show()

    def draw_circles(self, agent_loc, target, depth):
        # create painter instance with pixmap

        # draw current agent location
        self.penCentre = QtGui.QPen(QtCore.Qt.blue)
        self.penCentre.setWidth(3)
        self.painterInstance.setPen(self.penCentre)
        centre = QtCore.QPoint(*agent_loc)
        self.painterInstance.drawEllipse(centre, 2, 2)

        # draw circle at target location
        if target is not None:
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

    def draw_rects(self, text, spacing, agent_loc, rect):
        # self.painterInstance.restore()
        # create painter instance with pixmap

        # Coordinates for overlayed rectangle (ROI)
        xPos = rect[2]
        yPos = rect[0]
        xLen = rect[3] - xPos
        yLen = rect[1] - yPos

        # set rectangle color and thickness
        self.penRectangle = QtGui.QPen(QtCore.Qt.cyan)
        self.penRectangle.setWidth(3)
        # draw rectangle on painter
        self.painterInstance.setPen(self.penRectangle)
        self.painterInstance.drawRect(xPos,yPos,xLen,yLen)

        # Annotate rectangle
        self.painterInstance.setPen(QtCore.Qt.cyan)
        self.painterInstance.setFont(QFont('Decorative', min(abs(yLen)//12, 15)))
        self.painterInstance.drawText(xPos, yPos-8, "Agent")

        # # Add error message
        # self.painterInstance.setPen(QtCore.Qt.darkGreen)
        # self.painterInstance.setFont(QFont('Decorative', self.height//15))
        # self.painterInstance.drawText(self.width//10, self.height*17//20, text)
        # # Add spacing message
        # self.painterInstance.setPen(QtCore.Qt.darkGreen)
        # self.painterInstance.setFont(QFont('Decorative', self.height//15))
        # self.painterInstance.drawText(self.width*1//2, self.height*17//20, f'Spacing {spacing}')


    # def draw_point(self,x=0.0,y=0.0,z=0.0):
    #     x = self.img_height - x
    #     y = y
    #     # pyglet.graphics.draw(1, GL_POINTS,
    #     #     ('v2i', (x_new, y_new)),
    #     #     ('c3B', (255, 0, 0))
    #     # )
    #     glBegin(GL_POINTS) # draw point
    #     glVertex3f(x, y, z)
    #     glEnd()


    # def draw_circle(self, radius=10, res=30, pos_x=0, pos_y=0,
    #                 color=(1.0,1.0,1.0,1.0),**attrs):
    #
    #     points = []
    #     # window start indexing from bottom left
    #     x = self.img_height - pos_x
    #     y = pos_y
    #
    #     for i in range(res):
    #         ang = 2*math.pi*i / res
    #         points.append((math.cos(ang)*radius + y ,
    #                        math.sin(ang)*radius + x))
    #
    #     # draw filled polygon
    #     if   len(points) == 4 : glBegin(GL_QUADS)
    #     elif len(points)  > 4 : glBegin(GL_POLYGON)
    #     else: glBegin(GL_TRIANGLES)
    #     for p in points:
    #         # choose color
    #         glColor4f(color[0],color[1],color[2],color[3]);
    #         glVertex3f(p[0], p[1],0)  # draw each vertex
    #     glEnd()
    #     # reset color
    #     glColor4f(1.0, 1.0, 1.0, 1.0);
    #
    #
    # def draw_rect(self, x_min_init, y_min, x_max_init, y_max):
    #     main_batch = pyglet.graphics.Batch()
    #     # fix location
    #     x_max = self.img_height - x_max_init
    #     x_min = self.img_height - x_min_init
    #     # draw lines
    #     glColor4f(0.8, 0.8, 0.0, 1.0)
    #     main_batch.add(2, gl.GL_LINES, None,
    #                    ('v2f', (y_min, x_min, y_max, x_min)))
    #                    # ('c3B', (204, 204, 0, 0, 255, 0)))
    #     main_batch.add(2, gl.GL_LINES, None,
    #                    ('v2f', (y_min, x_min, y_min, x_max)))
    #                    # ('c3B', (204, 204, 0, 0, 255, 0)))
    #     main_batch.add(2, gl.GL_LINES, None,
    #                    ('v2f', (y_max, x_max, y_min, x_max)))
    #                    # ('c3B', (204, 204, 0, 0, 255, 0)))
    #     main_batch.add(2, gl.GL_LINES, None,
    #                    ('v2f', (y_max, x_max, y_max, x_min)))
    #                    # ('c3B', (204, 204, 0, 0, 255, 0)))
    #
    #     main_batch.draw()
    #     # reset color
    #     glColor4f(1.0, 1.0, 1.0, 1.0);
    #
    #
    #
    # def display_text(self, text, x, y, color=(0,0,204,255), #RGBA
    #                  anchor_x='left', anchor_y='top'):
    #     x = int(self.img_height - x)
    #     y = int(y)
    #     label = pyglet.text.Label(text,
    #                               font_name='Ariel', color=color,
    #                               font_size=8, bold=True,
    #                               x=y, y=x,
    #                               anchor_x=anchor_x, anchor_y=anchor_y)
    #     label.draw()


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

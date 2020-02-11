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

class Window(QMainWindow):
    """
    Window used as the main window for the application which integrate different widgets
    """
    def __init__(self, viewer_param):
        super().__init__()

        self.initUI(viewer_param)

    def initUI(self, viewer_param):
        """
        Main UI init element
        """
        # Status Bar
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("Start")
        
        # Menu Bar
        self.initMenu()
        
        # Image widget
        self.widget = SimpleImageViewer(arr=viewer_param["arrs"][0],
                                   arr_x=viewer_param["arrs"][1],
                                   arr_y=viewer_param["arrs"][2],
                                   filepath=viewer_param["filepath"])
        
        self.left_widget = SimpleImageViewerSettings()
        self.left_widget.setFrameShape(QFrame.StyledPanel)

        # Manage layout
        self.grid = QGridLayout()
        self.grid.addWidget(self.left_widget, 0, 0)
        self.grid.addWidget(self.widget, 0, 1)
        self.grid.setColumnStretch(1, 2) # default (later there will be event to change this when screen size change)
        self.grid.setColumnStretch(0, 1) # default
        # self.grid.addWidget(QWidget(), 0, 2) # Jamie's code

        self.layout_widget = QWidget()
        self.layout_widget.setLayout(self.grid)
        self.setCentralWidget(self.layout_widget)

        # Geometric window position and general setting
        self.resize(1000, 800)
        self.center()
        self.setWindowTitle('Reinforcement Learning - Medical')
        self.menubar.setStyleSheet("background:#D2D4DC; color:black")
        self.statusbar.setStyleSheet("background:#D2D4DC; color:black")
        self.show()
    
    def initMenu(self):
        # Menubar
        self.menubar = self.menuBar()
        
        # File menu
        file_menu = self.menubar.addMenu('&File')
        # Exit action in a file
        exitAct = QAction('Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)
        file_menu.addAction(exitAct)

        # Terminal menu
        terminal_menu = self.menubar.addMenu("&Terminal")
        
        # View menu
        view_menu = self.menubar.addMenu("&View")

        # Help menu
        help_menu = self.menubar.addMenu("&Help")

    def center(self):
        """
        Used to center the window automatically
        """
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
    
    def closeEvent(self, event):
        """
        Used to override close event and provide warning when closing application
        """        
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()  


class SimpleImageViewerSettings(QFrame):
    """
    Left widget controlling GUI elements settings.
    """    
    def __init__(self):
        super().__init__()

        # Widgets
        label_settings = QLabel("<b>SETTINGS</b>")
        label_run = QLabel("Run Agent")
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.buttonClicked)
        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setFocusPolicy(Qt.StrongFocus)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(5)

        hr = QLabel("<hr />")
        hr.setStyleSheet("margin: 10px 0")
        hr2 = QLabel("<hr />")
        hr2.setStyleSheet("margin: 10px 0")
        
        label_speed = QLabel("Agent Speed")
        self.setStyleSheet("font-family: sans-serif")
        label_run.setStyleSheet("margin-top: 10px")

        self.run_button.setStyleSheet("background-color:#4CAF50; color:white")

        # Layout
        vbox = QVBoxLayout()
        vbox.addWidget(label_settings)
        vbox.addWidget(label_run)
        vbox.addWidget(self.run_button)
        
        vbox.addWidget(hr)
        
        vbox.addWidget(label_speed)
        vbox.addWidget(self.speed_slider)

        vbox.addWidget(hr2)

        vbox.addStretch()

        self.setLayout(vbox)

    def buttonClicked(self):
        """
        Event handler (slot) for when the button is clicked
        """
        if self.run_button.text() == "Run":
            self.run_button.setText("Pause")
            self.run_button.setStyleSheet("background-color:#f44336; color:white")
        else:
            self.run_button.setText("Run")
            self.run_button.setStyleSheet("background-color:#4CAF50; color:white")


class SimpleImageViewer(QWidget):
    """
    Simple image viewer class for rendering images using pyglet and pyqt
    """
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
        self.img = QPixmap(qImg)
        self.img = self.img.scaledToWidth(350)
        self.img_x = QPixmap(qImg_x)
        self.img_x = self.img_x.scaledToWidth(350)
        self.img_y = QPixmap(qImg_y)
        self.img_y = self.img_y.scaledToWidth(350)

        self.label_img = QLabel()
        self.label_img_x = QLabel()
        self.label_img_x.setPixmap(self.img_x)
        self.label_img_y = QLabel()
        self.label_img_y.setPixmap(self.img_y)

        # Set background color for images to Black
        self.label_img.setAutoFillBackground(True)
        self.label_img_x.setAutoFillBackground(True)
        self.label_img_y.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.label_img.setPalette(p)
        self.label_img_x.setPalette(p)
        self.label_img_y.setPalette(p)

        # Initiliase Grid
        self.grid = QGridLayout()
        self.grid.addWidget(self.label_img, 0, 0)
        self.grid.addWidget(self.label_img_x, 0, 1)
        self.grid.addWidget(self.label_img_y, 1, 0)
        self.agent_signal.connect(self.agent_signal_handler)

        # Set Layout of GUI
        self.setLayout(self.grid)
        self.setWindowTitle("Landmark Detection Agent")
        
        # Stylesheet
        self.label_img.setStyleSheet("background: black; border:3px solid rgb(255, 0, 0); ")
        self.label_img_x.setStyleSheet("background: black; border:3px solid green; ")
        self.label_img_y.setStyleSheet("background: black; border:3px solid blue; ")

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
        _agent_loc = (agent_loc[1], self.height_x-agent_loc[2])
        rect_ = (self.height_x-rect[4], self.height_x-rect[5]) + rect[2:4]
        self.draw_rects(text, spacing, _agent_loc, rect_)
        self.draw_circles(_agent_loc, target, depth)
        self.painterInstance.end()

        self.painterInstance = QPainter(self.img_y)
        _agent_loc = (agent_loc[0]*self.width_y//self.height_y, self.height_y-agent_loc[2])       # Rotate 90 degrees ccw
        rect_ = (self.height_y-rect[4], self.height_y-rect[5]) + \
            (rect[0]*self.width_y//self.height_y, rect[1]*self.width_y//self.height_y)
        self.draw_rects(text, spacing, agent_loc, rect_)
        self.draw_circles(_agent_loc, target, depth)
        self.painterInstance.end()

        self.img = self.img.scaledToWidth(350)
        self.img_x = self.img_x.scaledToWidth(350)
        self.img_y = self.img_y.scaledToWidth(350)
        self.label_img.setPixmap(self.img)
        self.label_img_x.setPixmap(self.img_x)
        self.label_img_y.setPixmap(self.img_y)

    def draw_circles(self, agent_loc, target, depth):
        # Draw current agent location
        self.penCentre = QPen(Qt.cyan)
        self.penCentre.setWidth(4)
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
        self.painterInstance.setFont(QFont('Decorative', max(abs(yLen)//12, 15)))
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

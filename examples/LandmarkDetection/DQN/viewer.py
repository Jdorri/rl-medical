################################################################################
## PyQt GUI files containing codes for Windows and Widgets
# Author: Maleakhi, Alex, Faidon, Jamie
# Credit: Code adapted from Amir Alansary viewer.py file
################################################################################

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
from thread import WorkerThread
from functools import partial

from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

try:
    import pyglet
    from pyglet.gl import *
except ImportError as e:
    reraise(suffix="HINT: you can install pyglet directly via 'pip install pyglet'. But if you really just want to install all Gym dependencies and not have to think about it, 'pip install -e .[all]' or 'pip install gym[all]' will do it.")


################################################################################
## Main Window
# Integrate GUI application widgets and provide menus and windows functionalities.

class Window(QMainWindow):
    """
    Window used as the main window for the application which integrate different widgets.
    """
    # Signal for browse/ manual mode
    # Captures key pressed that will be used to store data for Human-in-the loop
    key_pressed = pyqtSignal(QEvent)

    def __init__(self, viewer_param, right_settings=None):
        super().__init__()
        self.initUI(viewer_param, right_settings)
        self.key_pressed.connect(self.on_key)

    def initUI(self, viewer_param, right_settings):
        """
        Main UI init element.
        """
        # Status Bar
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("Start")

        # Menu Bar
        self.initMenu()

        # Image widget (main widget)
        self.widget = SimpleImageViewer(arr=np.zeros(viewer_param["arrs"][0].shape),
                                   arr_x=np.zeros(viewer_param["arrs"][1].shape),
                                   arr_y=np.zeros(viewer_param["arrs"][2].shape),
                                   filepath=viewer_param["filepath"])

        # Left Settings widget
        if right_settings:
            self.left_widget = LeftWidgetSettings(self, True)
        else:
            self.left_widget = LeftWidgetSettings(self, False)
        self.left_widget.setFrameShape(QFrame.StyledPanel)

        # Right Settings widget
        if right_settings:
            self.right_widget = right_settings
        self.right_widget.setFrameShape(QFrame.StyledPanel)

        # Manage layout
        self.grid = QGridLayout()
        self.grid.addWidget(self.right_widget, 0, 11, 1, 1)
        self.grid.addWidget(self.left_widget, 0, 0, 1, 1) # (x, y, rowspan, colspan)
        self.grid.addWidget(self.widget, 0, 1, 1, 10)

        self.layout_widget = QWidget()
        self.layout_widget.setLayout(self.grid)
        self.setCentralWidget(self.layout_widget)

        # Geometric window position and general setting
        self.resize(1300, 800)
        self.center()
        self.setWindowTitle('Anatomical Landmark Detection')
        self.menubar.setStyleSheet("background:#D2D4DC; color:black")
        self.statusbar.setStyleSheet("background:#D2D4DC; color:black")
        self.show()

    def initMenu(self):
        """
        Used to initialise components related to menu bar.
        """
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

        # TODO: Add additional functionalities to menu bar
        # Terminal menu
        terminal_menu = self.menubar.addMenu("&Terminal")

        # View menu
        view_menu = self.menubar.addMenu("&View")

        # Night mode action
        nightModeAct = QAction("Night mode", self, checkable=True)
        nightModeAct.setStatusTip("Change layout to night mode")
        nightModeAct.triggered.connect(self.toggleMenu)
        view_menu.addAction(nightModeAct)

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

    def nightMode(self):
        "CSS Styling for night mode app version"
        # Overwrite widgets color
        self.setStyleSheet("background-color:black; color:white")
        self.left_widget.setStyleSheet("background-color:#1c1c1c")

    def dayMode(self):
        "CSS Styling for day mode app version"
        # Overwrite widgets color
        self.setStyleSheet("background-color:white; color:black")
        self.left_widget.setStyleSheet("background-color:white")

    def toggleMenu(self, state):
        "Event handler for toggle menu"
        if state:
            self.nightMode()
        else:
            self.dayMode()

    @pyqtSlot(QEvent)
    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.key_pressed.emit(event)

    def on_key(self, event):
        """
        Event handler methods for manual browsing functionality.
        Different actions for different keyPressEvents.
        Allows the user to move through the image by using arrow keys.
        """
        if self.right_widget.MODE == 'BROWSE MODE' and self.right_widget.env:
            if event.key() in {Qt.Key_W, Qt.Key_Up}:
                self.right_widget.on_clicking_up()
            elif event.key() in {Qt.Key_S, Qt.Key_Down}:
                self.right_widget.on_clicking_down()
            elif event.key() in {Qt.Key_A, Qt.Key_Left}:
                self.right_widget.on_clicking_left()
            elif event.key() in {Qt.Key_D, Qt.Key_Right}:
                self.right_widget.on_clicking_right()
            elif event.key() == Qt.Key_X:
                self.right_widget.on_clicking_zoomIn()
            elif event.key() == Qt.Key_Z:
                self.right_widget.on_clicking_zoomOut()

    def closeEvent(self, event):
        """
        Used to override close event and provide warning when closing application
        """
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


################################################################################
## Left Widget
# Control several of main application functionalities (positioned on the left of image widget).

class LeftWidgetSettings(QFrame):
    """
    Left widget controlling GUI elements settings.
    """

    def __init__(self, window, gui_launcher=False):
        super().__init__()
        # Width and height settings
        self.setMaximumWidth(400)
        self.setMinimumHeight(800)

        # Window object to access windows components
        self.window = window # Store window object to enable control over windows functionality

        self.title = QLabel("<b> Settings </b>")

        ## Default file mode
        self.simple_title = QLabel("<i> Load Default Data </i>")
        self.brain_button = QRadioButton("Brain")
        self.cardiac_button = QRadioButton("Cardiac")
        self.ultrasound_button = QRadioButton("Ultrasound")
        self.brain_button.setChecked(True)

        ## Advance file mode
        self.advance_title = QLabel("<i> Load Custom Data </i>")
        # Load model settings
        self.model_file = QLabel('Load Model', self)
        self.model_file_edit = QPushButton('Browse', self)
        self.model_file_edit_text = QLabel("No file selected")

        # Load landmark settings
        self.landmark_file = QLabel('Load Landmark', self)
        self.landmark_file_edit = QPushButton('Browse', self)
        self.landmark_file_edit_text = QLabel("No file selected")

        # Upload image settings
        self.img_file = QLabel('Upload Image', self)
        self.img_file_edit = QPushButton('Browse', self)
        self.img_file_edit_text = QLabel("No file selected")

        # Logo settings
        self.logo = QLabel()
        pixmap_logo = QPixmap("imperial_logo.png")
        pixmap_logo = pixmap_logo.scaledToHeight(64)
        self.logo.setPixmap(pixmap_logo)
        
        ## Manage layout
        # Default data settings layout
        hbox_simple = QHBoxLayout()
        hbox_simple.setSpacing(20)
        hbox_simple.addWidget(self.brain_button)
        hbox_simple.addWidget(self.cardiac_button)
        hbox_simple.addWidget(self.ultrasound_button)

        # Browse + Layout
        hbox_model = QHBoxLayout()
        hbox_model.setSpacing(20)
        hbox_model.addWidget(self.model_file_edit)
        hbox_model.addWidget(self.model_file_edit_text)
        
        hbox_image = QHBoxLayout()
        hbox_image.setSpacing(20)
        hbox_image.addWidget(self.img_file_edit)
        hbox_image.addWidget(self.img_file_edit_text)

        hbox_landmark = QHBoxLayout()
        hbox_landmark.setSpacing(20)
        hbox_landmark.addWidget(self.landmark_file_edit)
        hbox_landmark.addWidget(self.landmark_file_edit_text)

        # Main Layout
        vbox = QVBoxLayout()
        vbox.setSpacing(20)
        vbox.addWidget(self.title)
        vbox.addWidget(self.simple_title)
        vbox.addLayout(hbox_simple)
        vbox.addWidget(QLabel("<hr />"))
        vbox.addWidget(self.advance_title)
        vbox.addWidget(self.img_file)
        vbox.addLayout(hbox_image)
        vbox.addItem(QSpacerItem(300, 20))
        vbox.addWidget(self.landmark_file)
        vbox.addLayout(hbox_landmark)
        vbox.addItem(QSpacerItem(300, 20))
        vbox.addWidget(self.model_file)
        vbox.addLayout(hbox_model)
        vbox.addStretch()
        vbox.addWidget(self.logo)

        self.setLayout(vbox)

        # Event handler connection
        self.model_file_edit.clicked.connect(self.on_clicking_browse_model)
        self.landmark_file_edit.clicked.connect(self.on_clicking_browse_landmarks)
        self.img_file_edit.clicked.connect(self.on_clicking_browse_images)

        self.testing = False

    def on_clicking_browse_model(self):
        if not self.testing:
            self.fname_model = QFileDialog.getOpenFileName(self, "Browse Model",
                "./data/models", filter="*.data-*")
            filename = self.fname_model[0].split("/")
            self.model_file_edit_text.setText(filename[-1])

    def on_clicking_browse_landmarks(self):
        if not self.testing:
            self.fname_landmarks = QFileDialog.getOpenFileName(self, "Browse Landmark",
                "./data/filenames", filter="txt files (*landmark*.txt)")
            filename = self.fname_landmarks[0].split("/")
            self.landmark_file_edit_text.setText(filename[-1])

    def on_clicking_browse_images(self):
        if not self.testing:
            self.fname_images = QFileDialog.getOpenFileName(self, "Browse Image",
                "./data/filenames", filter="txt files (*test_files*.txt)")
            self.fname_images = QFileDialog.getOpenFileName(self, "Browse Image",
                "./data/filenames", filter="txt files (*landmarks*.txt)")
            


################################################################################
## Main Widget
# Responsible to draw images specified by settings and visualise agent's movement.

class SimpleImageViewer(QWidget):
    """
    Simple image viewer class for rendering images using pyglet and pyqt
    """
    agent_signal = pyqtSignal(dict) # Signaling agent move (current location, status)

    def __init__(self, arr, arr_x, arr_y, scale_x=1, scale_y=1, filepath=None, display=None):
        super().__init__()
        self.arrs = [arr, arr_x, arr_y]

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
        # TODO: resolve scaled to width later during final iteration (responsive)
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

        self.fig = plt.figure(figsize=(3, 6.0))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvas(self.fig)

        # Initiliase Grid
        self.grid = QGridLayout()
        self.grid.addWidget(self.label_img, 0, 0)
        self.grid.addWidget(self.label_img_x, 0, 1)
        self.grid.addWidget(self.label_img_y, 1, 0)
        self.grid.addWidget(self.canvas, 1, 1)
        self.agent_signal.connect(self.agent_signal_handler)

        # Set Layout of GUI
        self.setLayout(self.grid)
        self.setWindowTitle("Landmark Detection Agent")

        # Stylesheet
        self.label_img.setStyleSheet("background: black; border:3px solid rgb(255, 0, 0); ")
        self.label_img_x.setStyleSheet("background: black; border:3px solid green; ")
        self.label_img_y.setStyleSheet("background: black; border:3px solid blue; ")
        self.canvas.setStyleSheet("background: black; border:3px solid blue; ")

        # Style settings
        self.color_a = QColor(111, 230, 158)
        self.color_t = QColor(200, 100, 100)
        self.color_e = QColor(250, 250, 250)
        self.size_e = 20
        self.line_width = 1

        # agent trajactories
        self.x_traj = []
        self.y_traj = []
        self.z_traj = []
    
    def reset(self):
        """
        Reset
        """
        # Draw background image (brain)
        cvImg = self.arrs[0].astype(np.uint8)
        self.height, self.width, self.channel = cvImg.shape
        bytesPerLine = 3 * self.width
        qImg = QImage(cvImg.data, self.width, self.height, bytesPerLine, QImage.Format_RGB888)
        self.img = QPixmap(qImg) # can use this to scale the image: .scaled(450, 350, QtCore.Qt.KeepAspectRatio)

        cvImg_x = self.arrs[1].astype(np.uint8)
        self.height_x, self.width_x, self.channel_x = cvImg_x.shape
        bytesPerLine = 3 * self.width_x
        qImg_x = QImage(cvImg_x.data, self.width_x, self.height_x, bytesPerLine, QImage.Format_RGB888)
        self.img_x = QPixmap(qImg_x)

        cvImg_y = self.arrs[2].astype(np.uint8)
        self.height_y, self.width_y, self.channel_y = cvImg_y.shape
        bytesPerLine = 3 * self.width_y
        qImg_y = QImage(cvImg_y.data, self.width_y, self.height_y, bytesPerLine, QImage.Format_RGB888)
        self.img_y = QPixmap(qImg_y)

        # TODO: resolve scaled to width later during final iteration (responsive)
        self.img = self.img.scaledToWidth(350)
        self.img_x = self.img_x.scaledToWidth(350)
        self.img_y = self.img_y.scaledToWidth(350)
        self.label_img.setPixmap(self.img)
        self.label_img_x.setPixmap(self.img_x)
        self.label_img_y.setPixmap(self.img_y)
        
        # 3d plotting
        self.ax.clear()
        self.canvas.draw()

    def draw_image(self, arrs, agent_loc, target=None, rect=None, episode_end=False):
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
        _agent_loc, _rect, _target = self.translate(agent_loc, rect, target)
        self.drawer(_agent_loc, _rect, _target)
        self.painterInstance.end()

        self.painterInstance = QPainter(self.img_x)
        _agent_loc, _rect, _target = self.translate_x(agent_loc, rect, target)
        self.drawer(_agent_loc, _rect, _target)
        self.painterInstance.end()

        self.painterInstance = QPainter(self.img_y)
        _agent_loc, _rect, _target = self.translate_y(agent_loc, rect, target)
        self.drawer(_agent_loc, _rect, _target)
        self.painterInstance.end()

        if self.task in ['eval','browse']:
            self.draw_error()

        # TODO: resolve scaled to width later during final iteration (responsive)
        self.img = self.img.scaledToWidth(350)
        self.img_x = self.img_x.scaledToWidth(350)
        self.img_y = self.img_y.scaledToWidth(350)
        self.label_img.setPixmap(self.img)
        self.label_img_x.setPixmap(self.img_x)
        self.label_img_y.setPixmap(self.img_y)
        
        # 3d plotting
        if not episode_end:
            self.x_traj.append(agent_loc[0])
            self.y_traj.append(agent_loc[1])
            self.z_traj.append(agent_loc[2])
        else:
            self.x_traj = []
            self.y_traj = []
            self.z_traj = []
            self.ax.clear()

        self.ax.plot(self.x_traj,self.y_traj,self.z_traj, c="r")
        # self.ax.set_color("red")
        self.canvas.draw()

    def draw_error(self):
        """
        Error (mm) message during eval and browse mode.
        """
        self.painterInstance = QPainter(self.img)
        pen = QPen(self.color_e)
        # pen.setWidth(self.line_width * 2)
        self.painterInstance.setPen(pen)
        self.painterInstance.setFont(QFont("Arial", self.size_e))
        self.painterInstance.drawText(30, 30, f"Error: {self.error:.2f} mm")
        self.painterInstance.end()

    def drawer(self, agent_loc, rect, target):
        """
        Draw rectangle and target location (will be called by (draw_image) main drawer function)
        """
        xPos = rect[2]
        yPos = rect[0]
        xLen = rect[3] - xPos
        yLen = rect[1] - yPos

        rect_dims = [xPos,yPos,xLen,yLen,]
        hw_ratio = yLen / -xLen

        if self.task in ['eval','browse']:
            self.draw_point(target, self.color_t, width=12)

        self.draw_point(agent_loc, self.color_a)

        if self.task == 'browse':
            self.draw_crosshairs(agent_loc, hw_ratio)
        else:
            self.draw_rects(rect_dims)

    def translate(self, agent_loc, rect, target):
        """
        Agent movement Calculator (return value is used to draw rectangle/cross hair + agent location)
        """
        _agent_loc = (agent_loc[0], self.height-agent_loc[1])
        if target is not None:
            _target = (target[0], self.height-target[1])
        else:
            _target = None
        _rect = (self.height-rect[2], self.height-rect[3]) + rect[:2]

        return _agent_loc, _rect, _target

    def translate_x(self, agent_loc, rect, target):
        """
        Agent movement Calculator
        """
        _agent_loc = (agent_loc[1], self.height_x-agent_loc[2])
        if target is not None:
            _target = (target[1], self.height_x-target[2])
        else:
            _target = None
        _rect = (self.height_x-rect[4], self.height_x-rect[5]) + rect[2:4]

        return _agent_loc, _rect, _target

    def translate_y(self, agent_loc, rect, target):
        """
        Agent movement Calculator
        """
        _agent_loc = (agent_loc[0]*self.width_y//self.height_y, self.height_y-agent_loc[2])       # Rotate 90 degrees ccw
        if target is not None:
            _target = (target[0]*self.width_y//self.height_y, self.height_y-target[2])                # Rotate 90 degrees ccw
        else:
            _target = None
        _rect = (self.height_y-rect[4], self.height_y-rect[5]) + \
            (rect[0]*self.width_y//self.height_y, rect[1]*self.width_y//self.height_y)

        return _agent_loc, _rect, _target

    def draw_point(self, point_loc, color, width=7):
        """
        Draw target location
        """
        pen = QPen(color, width, cap=Qt.RoundCap)
        self.painterInstance.setPen(pen)
        self.painterInstance.drawPoint(QPoint(*point_loc))

    def draw_crosshairs(self, agent_loc, hw_ratio):
        """
        Cross hair draw method that will be used for browser mode/ HITL mode.
        """
        cross_len = 100
        hair_len = 3
        centre_space = 10
        c = QPoint(*agent_loc)

        pen = QPen(self.color_a)
        pen.setWidth(self.line_width)
        self.painterInstance.setPen(pen)

        for i in self.units():
            hw_ratio = hw_ratio if i[0] == 0 else 1

            vec = QPoint(*i)
            cross_s = c + centre_space * vec
            cross_s.setY(cross_s.y() * hw_ratio)
            cross_f = cross_s + cross_len * vec
            cross_f.setY(cross_f.y() * hw_ratio)
            self.painterInstance.drawLine(cross_s, cross_f)

            # Draw hairs
            for j in range(1,4):
                loc = cross_s + j * (cross_f - cross_s) / 4

                # Make crosshair thicker for correct resolution
                if self.scale == j:
                    pen.setWidth(3)
                    self.painterInstance.setPen(pen)

                if i[0] == 0:
                    hair_s = loc + pen.width() * hair_len * QPoint(-1,0)
                    hair_f = loc + pen.width() * hair_len * QPoint(+1,0)
                else:
                    hair_s = loc + pen.width() * hair_len * QPoint(0,-1)
                    hair_f = loc + pen.width() * hair_len * QPoint(0,+1)

                self.painterInstance.drawLine(hair_s, hair_f)

                # Reset pen width
                pen.setWidth(self.line_width)
                self.painterInstance.setPen(pen)

    def draw_rects(self, rect):
        """
        Draw rectangle surrounding agent in automatic mode.
        """
        corner_len = 25
        xPos, yPos, xLen, yLen = rect

        bL = QPoint(xPos, yPos)
        tL = QPoint(xPos, yPos + yLen)
        bR = QPoint(xPos + xLen, yPos)
        tR = QPoint(xPos + xLen, yPos + yLen)

        vecs = self.units()

        corners = {
            'bL': {'loc': bL, 'd1': QPoint(*vecs[0]), 'd2': QPoint(*vecs[1])},
            'tL': {'loc': tL, 'd1': QPoint(*vecs[0]), 'd2': QPoint(*vecs[3])},
            'bR': {'loc': bR, 'd1': QPoint(*vecs[2]), 'd2': QPoint(*vecs[1])},
            'tR': {'loc': tR, 'd1': QPoint(*vecs[2]), 'd2': QPoint(*vecs[3])},
        }

        pen = QPen(self.color_a)
        pen.setWidth(self.line_width * 2)
        self.painterInstance.setPen(pen)
        for k in corners.values():
            self.painterInstance.drawLine(k['loc'], k['loc'] + corner_len * k['d1'])
            self.painterInstance.drawLine(k['loc'], k['loc'] + corner_len * k['d2'])

        # # Annotate rectangle
        # self.painterInstance.setFont(QFont('Decorative', max(abs(yLen)//12, 15)))
        # self.painterInstance.drawText(xPos, yPos-8, "Agent ROI")

    def units(self):
        """
        Helper functions to return all corner of a unit squares.
        """
        return [[1,0],[0,-1],[-1,0],[0,1]]

    @pyqtSlot(dict)
    def agent_signal_handler(self, value):
        """
        Used to handle agent signal when it moves.
        """
        self.scale = value["scale"]
        self.task = value["task"]
        self.error = value["error"]
        self.is_terminal = value["is_terminal"]
        self.draw_image(
            arrs = value["arrs"],
            agent_loc = value["agent_loc"],
            target = value["target"],
            rect = value["rect"],
            episode_end = self.is_terminal
        )

    # def render(self):
        # self.window.flip()

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


################################################################################

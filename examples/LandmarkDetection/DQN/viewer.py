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

try:
    import pyglet
    from pyglet.gl import *
except ImportError as e:
    reraise(suffix="HINT: you can install pyglet directly via 'pip install pyglet'. But if you really just want to install all Gym dependencies and not have to think about it, 'pip install -e .[all]' or 'pip install gym[all]' will do it.")

################################################################################
## QMainWindow
class Window(QMainWindow):
    """
    Window used as the main window for the application which integrate different widgets.
    """
    KEY_PRESSED = pyqtSignal(QEvent)
    def __init__(self, viewer_param, app_settings=None):
        super().__init__()
        self.initUI(viewer_param, app_settings)
        self.KEY_PRESSED.connect(self.on_key)

    def initUI(self, viewer_param, app_settings):
        """
        Main UI init element.
        """
        # Status Bar
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("Start")

        # Menu Bar
        self.initMenu()

        # Image widget
        self.widget = SimpleImageViewer(arr=np.zeros(viewer_param["arrs"][0].shape),
                                   arr_x=np.zeros(viewer_param["arrs"][1].shape),
                                   arr_y=np.zeros(viewer_param["arrs"][2].shape),
                                   filepath=viewer_param["filepath"])

        # Left Settings widget
        if app_settings:
            self.left_widget = SimpleImageViewerSettings(self, True)
        else:
            self.left_widget = SimpleImageViewerSettings(self, False)
        self.left_widget.setFrameShape(QFrame.StyledPanel)

        # Right Settings widget
        if app_settings:
            self.right_widget = app_settings
            self.right_widget.setFrameShape(QFrame.StyledPanel)
        # self.left_widget.thread = self.right_widget.thread

        # Manage layout
        self.grid = QGridLayout()
        self.grid.addWidget(self.left_widget, 0, 0, 1, 1)
        self.grid.addWidget(self.widget, 0, 1, 1, 10)
        self.grid.addWidget(self.right_widget, 0, 11, 1, 1)
        # self.grid.setColumnStretch(1, 2) # default (later there will be event to change this when screen size change)
        # self.grid.setColumnStretch(0, 1) # default
        # if app_settings:
        #     self.grid.addWidget(self.right_widget, 0, 2) # for integration with Jamie's code

        self.layout_widget = QWidget()
        self.layout_widget.setLayout(self.grid)
        self.setCentralWidget(self.layout_widget)

        # Geometric window position and general setting
        self.resize(1300, 800)
        self.center()
        self.setWindowTitle('Reinforcement Learning - Medical')
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
        self.KEY_PRESSED.emit(event)

    def on_key(self, event):
        ''' Different actions for different keyPressEvents.
            Allows the user to move through the image by using arrow keys
        '''
        if self.right_widget.MODE == 'BROWSE MODE' and self.right_widget.env:
            # Browse mode key bindings
            if event.key() == Qt.Key_S:
                self.right_widget.on_clicking_in()
            elif event.key() == Qt.Key_A:
                self.right_widget.on_clicking_out()
            elif event.key() == Qt.Key_Up:
                self.right_widget.on_clicking_up()
            elif event.key() == Qt.Key_Down:
                self.right_widget.on_clicking_down()
            elif event.key() == Qt.Key_Left:
                self.right_widget.on_clicking_left()
            elif event.key() == Qt.Key_Right:
                self.right_widget.on_clicking_right()
            elif event.key() == Qt.Key_Space:
                self.right_widget.on_clicking_nextImg()
            elif event.key() == Qt.Key_Equal:
                self.right_widget.on_clicking_zoomIn()
            elif event.key() == Qt.Key_Minus:
                self.right_widget.on_clicking_zoomOut()

            # HITL mode additional key bindings
            if self.right_widget.HITL_mode.isChecked():
                if event.key() == Qt.Key_Backspace:
                    self.right_widget.on_clicking_HITLDelete()

    def closeEvent(self, event):
        """
        Used to override close event and provide warning when closing application
        """
        try:
            if self.right_widget.HITL and self.right_widget.env:
                self.right_widget.save_HITL()
        except AttributeError:
            pass
        event.accept()

    # def closeEvent(self, event):
    #     """
    #     Used to override close event and provide warning when closing application
    #     """
    #     reply = QMessageBox.question(self, 'Message',
    #         "Are you sure to quit?", QMessageBox.Yes |
    #         QMessageBox.No, QMessageBox.Yes)
    #
    #     if reply == QMessageBox.Yes:
    #         event.accept()
    #     else:
    #         event.ignore()

    # def setChildrenFocusPolicy(self, policy):
    #     '''Method to allow arrow keys to be caught in keyPressEvent()'''
    #     def recursiveSetChildFocusPolicy(parentQWidget):
    #         for childQWidget in parentQWidget.findChildren(QWidget):
    #             childQWidget.setFocusPolicy(policy)
    #             recursiveSetChildFocusPolicy(childQWidget)
    #     recursiveSetChildFocusPolicy(self)



################################################################################
## Left Widget
class SimpleImageViewerSettings(QFrame):
    """
    Left widget controlling GUI elements settings.
    """
    def __init__(self, window, gui_launcher=False):
        super().__init__()
        self.thread = WorkerThread(None) # Store thread to allow pause and run functionality
        self.window = window

        # Widgets
        # Label settings
        label_settings = QLabel("<b>SETTINGS</b>")
        label_run = QLabel("Pause Agent")
        hr = QLabel("<hr />")
        hr.setStyleSheet("margin: 10px 0")
        hr2 = QLabel("<hr />")
        hr2.setStyleSheet("margin: 10px 0")
        label_speed = QLabel("Agent Speed")
        # self.setStyleSheet("font-family: sans-serif")
        label_run.setStyleSheet("margin-top: 10px")

        # Button settings
        if gui_launcher:
            self.run_button = QPushButton("Pause")
            self.run_button.clicked.connect(self.buttonClicked)
            self.run_button.setStyleSheet("background-color:#f44336; color:white")
        else:
            self.run_button = QPushButton("Start")
            self.run_button.clicked.connect(self.buttonClicked)
            self.run_button.setStyleSheet("background-color:#4CAF50; color:white")

        # Slider settings
        self.speed_slider = QSlider(Qt.Horizontal, self)
        # self.speed_slider.setFocusPolicy(Qt.StrongFocus)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(5)
        self.speed_slider.setValue(5)
        self.speed_slider.valueChanged[int].connect(self.changeValue)

        # Manage layout
        vbox = QVBoxLayout()
        # First section
        vbox.addWidget(label_settings)
        vbox.addWidget(label_run)
        vbox.addWidget(self.run_button)
        vbox.addWidget(hr)

        # Second section
        vbox.addWidget(label_speed)
        vbox.addWidget(self.speed_slider)
        vbox.addWidget(hr2)

        # Third section
        vbox.addStretch()

        self.setLayout(vbox)

        # Flags for testing
        self.testing = False

    def buttonClicked(self):
        """
        Event handler (slot) for when the button is clicked
        """
        if self.run_button.text() == "Start":
            self.thread.start()
            self.run_button.setText("Pause")
            self.window.statusbar.showMessage("Run")
            self.run_button.setStyleSheet("background-color:#f44336; color:white")
        elif self.run_button.text() == "Resume":
            self.thread.pause = False
            self.run_button.setText("Pause")
            self.run_button.setStyleSheet("background-color:#f44336; color:white")
            self.window.statusbar.showMessage("Running")
        else:
            self.thread.pause = True
            self.run_button.setText("Resume")
            self.run_button.setStyleSheet("background-color:#4CAF50; color:white")
            self.window.statusbar.showMessage("Paused")

    def changeValue(self, value):
        """
        Event handler for slider (adjusting agent speed)
        """
        if value >= 4:
            self.thread.speed = WorkerThread.FAST
        elif value >= 2:
            self.thread.speed = WorkerThread.MEDIUM
        else:
            self.thread.speed = WorkerThread.SLOW


################################################################################
## Main Widget

class SimpleImageViewer(QWidget):
    """
    Simple image viewer class for rendering images using pyglet and pyqt
    """
    agent_signal = pyqtSignal(dict) # Signaling agent move (current location, status)

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

        # Style settings
        self.color_a = QColor(111, 230, 158)
        self.color_t = QColor(200, 100, 100)
        self.color_e = QColor(250, 250, 250)
        self.size_e = 20
        self.line_width = 1

    def draw_image(self, arrs, agent_loc, target=None, rect=None):
        """
        Main image drawer function
        """
        self.arr = arrs[0]
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
        self.draw_point(point_loc=(10,30), color=self.color_a)
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

    def draw_error(self):
        self.painterInstance = QPainter(self.img)
        pen = QPen(self.color_e)
        # pen.setWidth(self.line_width * 2)
        self.painterInstance.setPen(pen)
        self.painterInstance.setFont(QFont("Arial", self.size_e))
        self.painterInstance.drawText(30, 30, f"Error: {self.error:.2f} mm")
        self.painterInstance.end()


    def drawer(self, agent_loc, rect, target):
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
        # _agent_loc = (agent_loc[0], self.height-agent_loc[1])
        # _agent_loc = (self.height-agent_loc[1], self.width-agent_loc[0])
        _agent_loc = (self.width-agent_loc[1], self.height-agent_loc[0])
        print(agent_loc, _agent_loc)
        if target is not None:
            # _target = (target[0], self.height-target[1])
            # _target = (self.height-target[1], self.width-target[0])
            _target = (self.width-target[1], self.height-target[0])
        else:
            _target = None
        _rect = (self.height-rect[2], self.height-rect[3]) + rect[:2]
        return _agent_loc, _rect, _target

    def translate_x(self, agent_loc, rect, target):
        _agent_loc = (agent_loc[1], self.height_x-agent_loc[2])
        if target is not None:
            _target = (target[1], self.height_x-target[2])
        else:
            _target = None
        _rect = (self.height_x-rect[4], self.height_x-rect[5]) + rect[2:4]
        return _agent_loc, _rect, _target

    def translate_y(self, agent_loc, rect, target):
        _agent_loc = (agent_loc[0]*self.width_y//self.height_y, self.height_y-agent_loc[2])       # Rotate 90 degrees ccw
        if target is not None:
            _target = (target[0]*self.width_y//self.height_y, self.height_y-target[2])                # Rotate 90 degrees ccw
        else:
            _target = None
        _rect = (self.height_y-rect[4], self.height_y-rect[5]) + \
            (rect[0]*self.width_y//self.height_y, rect[1]*self.width_y//self.height_y)
        return _agent_loc, _rect, _target

    def draw_point(self, point_loc, color, width=7):
        pen = QPen(color, width, cap=Qt.RoundCap)
        self.painterInstance.setPen(pen)
        self.painterInstance.drawPoint(QPoint(*point_loc))

    def draw_crosshairs(self, agent_loc, hw_ratio):
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
        return [[1,0],[0,-1],[-1,0],[0,1]]

    @pyqtSlot(dict)
    def agent_signal_handler(self, value):
        """
        Used to handle agent signal when it moves.
        """
        self.scale = value["scale"]
        self.task = value["task"]
        self.error = value["error"]
        self.draw_image(
            arrs = value["arrs"],
            agent_loc = value["agent_loc"],
            target = value["target"],
            rect = value["rect"]
        )

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

    # def draw_circles(self, agent_loc, target, depth):
    #     # Draw current agent location
    #     self.penCentre = QPen(Qt.cyan)
    #     self.penCentre.setWidth(4)
    #     self.painterInstance.setPen(self.penCentre)
    #     centre = QPoint(*agent_loc)
    #     self.painterInstance.drawEllipse(centre, 2, 2)
    #
    #     # Draw circle at target location
    #     if target is not None:
    #         self.penCentre = QPen(Qt.red)
    #         self.penCentre.setWidth(3)
    #         self.painterInstance.setPen(self.penCentre)
    #         centre = QPoint(*target)
    #         self.painterInstance.drawEllipse(centre, 2, 2)
    #
    #         # draw circle surrounding target
    #         self.penCirlce = QPen(QColor(255,0,0,0))
    #         self.penCirlce.setWidth(3)
    #         self.painterInstance.setPen(self.penCirlce)
    #         self.painterInstance.setBrush(Qt.red)
    #         self.painterInstance.setOpacity(0.2)
    #         centre = QPoint(*target)
    #         radx = rady = depth * 30
    #         self.painterInstance.drawEllipse(centre, radx, rady)


################################################################################

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

from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

################################################################################
## Main Widget
# Responsible to draw images specified by settings and visualise agent's movement.

class SimpleImageViewer(QWidget):
    """
    Simple image viewer class for rendering images using pyqt
    """
    agent_signal = pyqtSignal(dict) # Signaling agent move (current location, status)

    def __init__(self, arrs, scale_x=1, scale_y=1, filepath=None, window=None):
        super().__init__()
        self.arrs = arrs
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.window = window

        # Rotation flag (mainly for fetal)
        self.rotate = False

        # Set image formatting and get shape
        cvImg, cvImg_x, cvImg_y = self.get_imgs(self.arrs)

        # initialize window with the input image
        assert self.arrs[0].shape == (self.height, self.width, 3), "You passed in an image with the wrong shape"

        # Convert image to correct format
        bytesPerLine = 3 * self.width
        qImg = QImage(cvImg.data, self.width, self.height, bytesPerLine, QImage.Format_RGB888)
        bytesPerLine = 3 * self.width_x
        qImg_x = QImage(cvImg_x.data, self.width_x, self.height_x, bytesPerLine, QImage.Format_RGB888)
        bytesPerLine = 3 * self.width_y
        qImg_y = QImage(cvImg_y.data, self.width_y, self.height_y, bytesPerLine, QImage.Format_RGB888)

        # Initialise images with labels
        self.img = QPixmap(qImg)
        self.img = self.img.scaled(400, 400, QtCore.Qt.KeepAspectRatio)
        self.img_x = QPixmap(qImg_x)
        self.img_x = self.img_x.scaled(400, 400, QtCore.Qt.KeepAspectRatio)
        self.img_y = QPixmap(qImg_y)
        self.img_y = self.img_y.scaled(400, 400, QtCore.Qt.KeepAspectRatio)

        self.label_img = QLabel()
        self.label_img.setPixmap(self.img)
        self.label_img_x = QLabel()
        self.label_img_y = QLabel()
        self.label_img_y.setPixmap(self.img_y)
        self.label_img.setMinimumSize(400, 400)
        self.label_img_x.setMinimumSize(400, 400)
        self.label_img_y.setMinimumSize(400, 400)

        # Set background color for images to Black
        self.label_img.setAutoFillBackground(True)
        self.label_img_x.setAutoFillBackground(True)
        self.label_img_y.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.label_img.setPalette(p)
        self.label_img_x.setPalette(p)
        self.label_img_y.setPalette(p)

        # 3D Plot settings
        self.fig = plt.figure(figsize=(3, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvas(self.fig)

        # Agent trajactories storage
        self.x_traj = []
        self.y_traj = []
        self.z_traj = []
        self.tgt_x = []
        self.tgt_y = []
        self.tgt_z = []

        # Setup layout
        self.grid = self.generate_layout("BrainMRI") # generate default

        self.agent_signal.connect(self.agent_signal_handler)

        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.grid)
        self.setLayout(self.main_layout)

        # Stylesheet settings
        self.label_img.setStyleSheet("background: black; border:3px solid #DD2501; ")
        self.label_img_x.setStyleSheet("background: black; border:3px solid #66A40A; ")
        self.label_img_y.setStyleSheet("background: black; border:3px solid #006EAF; ")
        self.setStyleSheet("background: white")

        # Style settings
        self.color_a = QColor(111, 230, 158)
        self.color_t = QColor(200, 100, 100)
        self.color_e = QColor(250, 250, 250)
        self.size_e = 18
        self.line_width = 1
    
    def generate_layout(self, usecase):
        """
        Return appropriate layout according to usecase (Brain|Cardiac|Fetal)
        """
        # Generate layout for brain and fetal
        if usecase in {"BrainMRI", "FetalUS"}:
            grid = QGridLayout()
            grid.addWidget(self.label_img, 0, 0)
            grid.addWidget(self.label_img_x, 0, 1)
            grid.addWidget(self.label_img_y, 1, 0)
            grid.addWidget(self.canvas, 1, 1)

            return grid
        else:
            grid = QGridLayout()
            grid.addWidget(self.label_img, 1, 1)
            grid.addWidget(self.label_img_x, 0, 1)
            grid.addWidget(self.label_img_y, 1, 0)
            grid.addWidget(self.canvas, 0, 0)

            return grid

    def reset(self):
        """
        Reset the gui to black image (initial)
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

        self.img = self.img.scaled(400, 400, QtCore.Qt.KeepAspectRatio)
        self.img_x = self.img_x.scaled(400, 400, QtCore.Qt.KeepAspectRatio)
        self.img_y = self.img_y.scaled(400, 400, QtCore.Qt.KeepAspectRatio)
        self.label_img.setPixmap(self.img)
        self.label_img_x.setPixmap(self.img_x)
        self.label_img_y.setPixmap(self.img_y)

        self.clear_3d()
        self.window.right_widget.automatic_mode.clear_2d()

    def clear_3d(self):
        """
        Used to clear 3d trajectories
        """
        self.x_traj = []
        self.y_traj = []
        self.z_traj = []
        self.tgt_x = []
        self.tgt_y = []
        self.tgt_z = []
        self.ax.clear()
        self.set_3d_axes(self.ax,self.x_lim,self.y_lim,self.z_lim)
        self.canvas.draw()


    def draw_image(self, arrs, agent_loc, target=None, rect=None, episode_end=False):
        """
        Main image drawer function
        """
        cvImg, cvImg_x, cvImg_y = self.get_imgs(arrs)

        bytesPerLine = 3 * self.width
        qImg = QImage(cvImg.data, self.width, self.height, bytesPerLine, QImage.Format_RGB888)
        bytesPerLine = 3 * self.width_x
        qImg_x = QImage(cvImg_x.data, self.width_x, self.height_x, bytesPerLine, QImage.Format_RGB888)
        bytesPerLine = 3 * self.width_y
        qImg_y = QImage(cvImg_y.data, self.width_y, self.height_y, bytesPerLine, QImage.Format_RGB888)

        self.img = QPixmap(qImg)
        self.img_x = QPixmap(qImg_x)
        self.img_y = QPixmap(qImg_y)

        # Draw rectangles and agent (overlay)
        self.painterInstance = QPainter(self.img)
        # Rotate if needed
        if self.window.usecase == 'FetalUS':
            self.rotate = True
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

        # Draw error in evaluation and browser mode
        if self.task in ['eval','browse']:
            self.draw_error()

        # Set image that has been drawn
        self.img = self.img.scaled(400, 400, QtCore.Qt.KeepAspectRatio)
        self.img_x = self.img_x.scaled(400, 400, QtCore.Qt.KeepAspectRatio)
        self.img_y = self.img_y.scaled(400, 400, QtCore.Qt.KeepAspectRatio)
        self.label_img.setPixmap(self.img)
        self.label_img.setAlignment(QtCore.Qt.AlignCenter)
        self.label_img_x.setPixmap(self.img_x)
        self.label_img_x.setAlignment(QtCore.Qt.AlignCenter)
        self.label_img_y.setPixmap(self.img_y)
        self.label_img_y.setAlignment(QtCore.Qt.AlignCenter)

        # 3d plotting
        self.x_lim = self.width
        self.y_lim = self.height
        self.z_lim = self.height_x
        
        if target != None:
            self.tgt_x.append(target[0])
            self.tgt_y.append(target[1])
            self.tgt_z.append(target[2])
        if not episode_end:
            self.x_traj.append(agent_loc[0])
            self.y_traj.append(agent_loc[1])
            self.z_traj.append(agent_loc[2])

            # 2D Trajectory
            if self.window.right_widget.automatic_mode.which_task() != "Play":
                self.window.right_widget.automatic_mode.x.append(self.cnt)
                self.window.right_widget.automatic_mode.y.append(self.error)
        else:
            self.clear_3d()
            self.window.right_widget.automatic_mode.clear_2d()

        self.ax.plot(self.x_traj,self.y_traj,self.z_traj, c="#0091D4", linewidth=1.5)
        self.ax.plot(self.tgt_x,self.tgt_y,self.tgt_z, marker='x', c='green', linewidth=1.5)
        self.set_3d_axes(self.ax,self.x_lim,self.y_lim,self.z_lim)
        self.canvas.draw()

        if self.window.right_widget.automatic_mode.which_task() != "Play":
            self.window.right_widget.automatic_mode.ax.plot(self.window.right_widget.automatic_mode.x, self.window.right_widget.automatic_mode.y, c="orange")
            self.window.right_widget.automatic_mode.canvas.draw()

    def set_3d_axes(self, ax, x_lim, y_lim, z_lim):
        """
        Sets the axis labels and limits.
        """
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        ax.set_xlim(0, x_lim)
        ax.set_ylim(0, y_lim)
        ax.set_zlim(0, z_lim)

    def which_size_error_text(self):
        """
        Determine size of text depending on usecase
        """
        if self.window.usecase == "BrainMRI":
            self.size_e = 18
        elif self.window.usecase == "CardiacMRI":
            self.size_e = 25
        else:
            self.size_e = 25

    def get_imgs(self, arrs):
        if self.window.usecase in ['BrainMRI', 'CardiacMRI']:
            cvImg = arrs[0].astype(np.uint8)
            cvImg_x = arrs[1].astype(np.uint8)
            cvImg_y = arrs[2].astype(np.uint8)
        elif self.window.usecase == 'FetalUS':
            cvImg = arrs[0].astype(np.uint8)
            cvImg_x = arrs[2].astype(np.uint8)
            cvImg_y = arrs[1].astype(np.uint8)

        self.height, self.width, self.channel = cvImg.shape
        self.height_x, self.width_x, self.channel_x = cvImg_x.shape
        self.height_y, self.width_y, self.channel_y = cvImg_y.shape

        return cvImg, cvImg_x, cvImg_y

    def translate(self, agent_loc, rect, target):
        ''' 2 step process:
                - change from agent coords into img coords. Img coords
                start from top left, agent coords start from bottom right. So
                need to do (x,y) -> (y,x) for agent coords
                - Perform relevant rotation (i.e. 90 degrees ccw)
        '''
        if self.window.usecase in ['BrainMRI', 'CardiacMRI']:
            _agent_loc = (agent_loc[0], self.height-agent_loc[1])
            if target is not None:
                _target = (target[0], self.height-target[1])
            else:
                _target = None
            _rect = (self.height-rect[2], self.height-rect[3]) + rect[:2]

        elif self.window.usecase == 'FetalUS':
            _agent_loc = agent_loc[1::-1]
            if target is not None:
                _target = target[1::-1]
            else:
                _target = None
            _rect = rect[:4]

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
        _agent_loc = (agent_loc[0], self.height_y-agent_loc[2])       # Rotate 90 degrees ccw
        if target is not None:
            _target = (target[0], self.height_y-target[2])                # Rotate 90 degrees ccw
        else:
            _target = None
        _rect = (self.height_y-rect[4], self.height_y-rect[5]) + rect[:2]
        return _agent_loc, _rect, _target

    def draw_error(self):
        """
        Error (mm) message during eval and browse mode.
        """
        self.painterInstance = QPainter(self.img)
        pen = QPen(self.color_e)
        self.painterInstance.setPen(pen)
        self.which_size_error_text() # determine size of pen
        self.painterInstance.setFont(QFont("Arial", self.size_e))

        # Change positioning of error label depending on usecase
        if self.window.usecase in {"BrainMRI", "CardiacMRI"}:
            self.painterInstance.drawText(0, 30, f"Error: {self.error:.2f} mm")
        else:
            self.painterInstance.drawText(0, 22, f"Error: {self.error:.2f} mm")
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
        hw_ratio = abs(yLen / xLen)

        if self.task in ['eval','browse']:
            w = 12 if self.window.usecase == 'BrainMRI' else 16
            self.draw_point(target, self.color_t, width=w)

        self.draw_point(agent_loc, self.color_a)

        if self.task == 'browse':
            self.draw_crosshairs(agent_loc, hw_ratio)
        else:
            self.draw_rects(rect_dims)

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

        if self.rotate:
            tL = QPoint(xPos, yPos)
            bL = QPoint(xPos, yPos + yLen)
            tR = QPoint(xPos + xLen, yPos)
            bR = QPoint(xPos + xLen, yPos + yLen)
            self.rotate = False
        else:
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

        # # Annotate rectangle (uncomment if wish to use this)
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
        Used to handle agent signal when agent moves.
        """
        self.scale = value["scale"]
        self.task = value["task"]
        self.error = value["error"]
        self.is_terminal = value["is_terminal"]
        self.cnt = value["cnt"]
        self.draw_image(
            arrs = value["arrs"],
            agent_loc = value["agent_loc"],
            target = value["target"],
            rect = value["rect"],
            episode_end = self.is_terminal
        )

################################################################################
## 3D Plot widget
# Author: Maleakhi, Alex, Faidon, Jamie, Olle, Harry
################################################################################

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


###############################################################################
## 3D Trajectories Plot
# Display agent's trajectories

class Plot3D(QWidget):
    """
    Class to plot agent's trajectories.
    """

    def __init__(self):
        
        super().__init__()

        # 3D Plot settings
        self.window = None
        self.fig = plt.figure(figsize=(3, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvas(self.fig)

        # Agent trajactories storage
        self.x_traj = []
        self.y_traj = []
        self.z_traj = []

        # Target storage
        self.tgt_x = []
        self.tgt_y = []
        self.tgt_z = []

        # Manage layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)

        self.setLayout(vbox)
    
    def add_trajectories(self, x, y, z):
        """
        Add trajectories

        :param x: x value to be added
        :param y: y value to be added
        :param z: z value to be added
        """

        self.x_traj.append(x)
        self.y_traj.append(y)
        self.z_traj.append(z)
    
    def add_target(self, target):
        """
        Add target coordinates.

        :param target: array of targets
        """

        if target is not None:
            self.tgt_x.append(target[0])
            self.tgt_y.append(target[1])
            self.tgt_z.append(target[2])
        
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

        width = self.window.widget.width
        height = self.window.widget.height
        height_x = self.window.widget.height_x

        self.ax.clear()
        self.set_3d_axes(self.ax, width, height, height_x)
        self.canvas.draw()
    
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
    
    def draw(self):
        """
        Draw plots
        """

        width = self.window.widget.width
        height = self.window.widget.height
        height_x = self.window.widget.height_x

        self.ax.plot(self.x_traj,self.y_traj,self.z_traj, c="#0091D4", linewidth=1.5)
        self.ax.plot(self.tgt_x,self.tgt_y,self.tgt_z, marker='x', c='green', linewidth=1.5)
        self.set_3d_axes(self.ax, width, height, height_x)
        self.canvas.draw()
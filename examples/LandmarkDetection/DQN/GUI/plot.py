################################################################################
## Error Plot Widget
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
## 2D Error Plot
# Display distance error against steps

class Plot(QWidget):
    """
    Class to plot distance error vs steps.
    """

    def __init__(self):
        
        super().__init__()

        # Initialise matplotlib figure
        self.fig = plt.figure(figsize=(4, 3))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.ax.set_xlabel("Steps", fontsize=8)
        self.ax.set_ylabel("Distance Error", fontsize=8)
        self.fig.tight_layout()
        self.ax.tick_params(axis="both", labelsize=6)

        # Trajectory storage
        self.x = []
        self.y = []

        # Manage layout
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("<hr />"))
        vbox.addItem(QSpacerItem(300, 20))
        vbox.addWidget(QLabel("<i>Error Plot</i>"))
        vbox.addWidget(self.canvas)

        self.setLayout(vbox)
    
    def add_trajectories(self, x, y):
        """
        Add trajectories

        :param x: x value to be added
        :param y: y value to be added
        """

        self.x.append(x)
        self.y.append(y)
    
    def clear_2d(self):
        """
        Used to clear 2d trajectories
        """

        self.x = []
        self.y = []
        self.ax.clear()
        self.ax.set_xlabel("Steps", fontsize=8)
        self.ax.set_ylabel("Distance Error", fontsize=8)
        self.ax.tick_params(axis="both", labelsize=6)
        self.canvas.draw()
    
    def draw(self):
        """
        Draw plots
        """

        self.ax.plot(self.x, self.y, c="orange")
        self.canvas.draw()
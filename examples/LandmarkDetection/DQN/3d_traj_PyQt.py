import sys
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class Trajectory3D(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        self.example_traj_x = [210,210,210,210,210,192,192,174,156,174]
        self.example_traj_y = [258,240,240,222,222,202,204,204,204,204]
        self.example_traj_z = [102,102,120,120,138,138,138,138,138,138]

        self.setWindowTitle('Testing (3D) matplotlib plot')

        self.fig = plt.figure(figsize=(8.0,8.0))
        self.canvas = FigureCanvas(self.fig)

        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.plot(self.example_traj_x,self.example_traj_y,self.example_traj_z)
        self.canvas.draw()

        layout.addWidget(self.canvas)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Trajectory3D()
    window.show()
    app.exec_()

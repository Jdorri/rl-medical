################################################################################
## Window GUI file used to integrate various widgets 
# Author: Maleakhi, Alex, Jamie, Faidon
################################################################################

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from viewer import SimpleImageViewer
from left_widget import LeftWidgetSettings

import numpy as np

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

    def __init__(self, viewer_param, right_widget=None):
        super().__init__()
        self.init_UI(viewer_param, right_widget)
        self.key_pressed.connect(self.on_key)

    def init_UI(self, viewer_param, right_widget):
        """
        Main UI init element.
        """
        # Indication of usecase (data_type)
        # Default: BrainMRI
        self.usecase = "BrainMRI" # can be BrainMRI, CardiacMRI, or FetalUS

        # Status Bar
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("Ready")

        # Initialise main widget
        arrs = [
            np.zeros(viewer_param["arrs"][0].shape),
            np.zeros(viewer_param["arrs"][1].shape),
            np.zeros(viewer_param["arrs"][2].shape)
        ]
        self.widget = SimpleImageViewer(arrs=arrs,
                                        filepath=viewer_param["filepath"],
                                        window=self)

        # Initialise left widget
        self.left_widget = LeftWidgetSettings(self)
        self.left_widget.setFrameShape(QFrame.StyledPanel)

        # Initialise right widget
        if right_widget:
            self.right_widget = right_widget
        self.right_widget.setFrameShape(QFrame.StyledPanel)

        # Create layout
        self.grid = QGridLayout()
        self.grid.addWidget(self.right_widget, 0, 11, 1, 1)
        self.grid.addWidget(self.left_widget, 0, 0, 1, 1) # (x, y, rowspan, colspan)
        self.grid.addWidget(self.widget, 0, 1, 1, 10)

        self.layout_widget = QWidget()
        self.layout_widget.setLayout(self.grid)
        self.setCentralWidget(self.layout_widget)

        # Geometric window position and general setting
        self.showMaximized()
        self.setWindowTitle('Anatomical Landmark Detection')

        # Menu Bar
        self.init_menu()
        
        # CSS Styling for windows
        self.statusbar.setStyleSheet("background:#003E74; color:white")
        self.setStyleSheet("""
            QMenuBar {
                background:#003E74; color: white; padding: 5px 0 
            }

            QMenuBar::item::disabled {
                color: grey !important;
            }
        """)

    def init_menu(self):
        """
        Used to initialise components related to menu bar.
        """
        # Menubar
        self.menubar = self.menuBar()

        ## File menu
        file_menu = self.menubar.addMenu('&File')

        # Load action
        self.load_model_action = QAction("Load Model", self)
        self.load_model_action.setShortcut("Ctrl+M")
        self.load_model_action.triggered.connect(self.left_widget.on_clicking_browse_model)

        self.load_image_action = QAction("Load Image(s)", self)
        self.load_image_action.setShortcut("Ctrl+I")
        self.load_image_action.triggered.connect(self.left_widget.on_clicking_browse_images)

        self.load_landmark_action = QAction("Load Landmark(s)", self)
        self.load_landmark_action.setShortcut("Ctrl+L")
        self.load_landmark_action.triggered.connect(self.left_widget.on_clicking_browse_landmarks)

        # Exit action in a file
        exitAct = QAction('Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)

        # Integrate into menu bar
        file_menu.addAction(self.load_model_action)
        file_menu.addAction(self.load_image_action)
        file_menu.addAction(self.load_landmark_action)
        file_menu.addSeparator()
        file_menu.addAction(exitAct)

        ## Terminal menu
        terminal_menu = self.menubar.addMenu("&Terminal")

        # Load action
        show_terminal_action = QAction("Show Terminal", self, checkable=True)
        show_terminal_action.setChecked(True)
        show_terminal_action.triggered.connect(self.on_show_terminal)

        terminal_menu.addAction(show_terminal_action)

        ## Help menu
        help_menu = self.menubar.addMenu("&Help")

        # Help action
        help_action = QAction("Application Help", self)
        help_action.setShortcut("Ctrl+H")
        help_action.triggered.connect(self.show_full_help)

        help_menu.addAction(help_action)

    def show_full_help(self):
        # Will open a new help window
        pass

    def on_show_terminal(self, state):
        if state:
            # Show terminal
            pass
        else:
            # Dont show terminal
            pass

    @pyqtSlot(QEvent)
    def keyPressEvent(self, event):
        """
        Capture and handle keyboard key press events
        """
        super().keyPressEvent(event)
        self.key_pressed.emit(event)

    def on_key(self, event):
        """
        Event handler methods for manual browsing functionality.
        Different actions for different keyPressEvents.
        Allows the user to move through the image by using arrow keys.
        """
        if self.right_widget.get_mode() == self.right_widget.BROWSE_MODE and self.right_widget.browse_mode.env:
            if event.key() in {Qt.Key_W, Qt.Key_Up}:
                self.right_widget.browse_mode.y_action.on_clicking_up()
            elif event.key() in {Qt.Key_S, Qt.Key_Down}:
                self.right_widget.browse_mode.y_action.on_clicking_down()
            elif event.key() in {Qt.Key_A, Qt.Key_Left}:
                self.right_widget.browse_mode.x_action.on_clicking_left()
            elif event.key() in {Qt.Key_D, Qt.Key_Right}:
                self.right_widget.browse_mode.x_action.on_clicking_right()
            elif event.key() == Qt.Key_Equal:
                self.right_widget.browse_mode.on_clicking_zoomIn()
            elif event.key() == Qt.Key_Minus:
                self.right_widget.browse_mode.on_clicking_zoomOut()
            elif event.key() == Qt.Key_Z:
                self.right_widget.browse_mode.z_action.on_clicking_in()
            elif event.key() == Qt.Key_X:
                self.right_widget.browse_mode.z_action.on_clicking_out()
            elif event.key() == Qt.Key_Space:
                self.right_widget.browse_mode.on_clicking_nextImg()

            # HITL mode additional key bindings
            if self.right_widget.browse_mode.HITL_mode.isChecked():
                if event.key() == Qt.Key_Backspace:
                    self.right_widget.browse_mode.on_clicking_HITLDelete()

    def closeEvent(self, event):
        """
        Used to override close event and provide warning when closing application
        """
        # reply = QMessageBox.question(self, 'Message',
        #     "Are you sure to quit?", QMessageBox.Yes |
        #     QMessageBox.No, QMessageBox.Yes)
        
        # Save HITL file
        try:
            if self.right_widget.get_mode() == self.right_widget.BROWSE_MODE:
                if self.right_widget.browse_mode.HITL and self.right_widget.browse_mode.env:
                    self.right_widget.browse_mode.save_HITL()
        except AttributeError:
            pass

        # if reply == QMessageBox.Yes:
        #     event.accept()
        # else:
        #     event.ignore()
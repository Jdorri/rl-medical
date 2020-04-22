################################################################################
## Doorway to launch application's GUI
# Author: Maleakhi, Alex, Jamie, Faidon
################################################################################

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from dataReader import *

from DQN import get_viewer_data

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn
warnings.simplefilter("ignore", category=PendingDeprecationWarning)

import sys

from window import Window
from right_widget_automatic import RightWidgetSettings
from right_widget_browse import RightWidgetSettingsBrowseMode

from FilenamesGUI import FilenamesGUI


###############################################################################
## Controller class 
# Responsible to run the entire application

class Controller:
    def __init__(self, display=True):
        self.app = QApplication(sys.argv)
        self.viewer_param = get_viewer_data()

        # Initialise the right settings tab
        self.right_widget = Tab()

        # Initialise the window
        self.window = Window(self.viewer_param, self.right_widget)
        self.right_widget.automatic_mode.window = self.window
        self.right_widget.browse_mode.window = self.window
        
        # Show window
        self.window.show()


###############################################################################
## Tab Widget
# Responsible to integrate automatic mode and browse mode through tab functionality

class Tab(QFrame):
    AUTOMATIC_MODE = "AUTOMATIC"
    BROWSE_MODE = "BROWSE"

    def __init__(self):
        super().__init__()
        # Create tab widget that integrates automatic and browse mode
        self.tab_widget = QTabWidget()

        # Right widgets initialisation
        self.automatic_mode = RightWidgetSettings()
        self.browse_mode = RightWidgetSettingsBrowseMode()

        # Tab settings
        self.tab_widget.addTab(self.automatic_mode, "Automatic Mode")
        self.tab_widget.addTab(self.browse_mode, "Browse Mode")

        # Layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.tab_widget)
        self.setLayout(vbox)

        # Event handler
        self.tab_widget.currentChanged.connect(self.on_change)

        # Responsive
        self.setMaximumWidth(400)
        self.setStyleSheet("background:#EBEEEE")
    
    def save_HITL(self):
        ''' Method to save HITL if appropriate '''
        try:
            if self.browse_mode.env and self.browse_mode.HITL:
                self.browse_mode.save_HITL()
        except AttributeError:
            pass
    
    @pyqtSlot(int)
    def on_change(self, index):
        # If automatic mode is selected, reset image and other relevant flags
        if index == 0:
            # Save HITL status
            self.save_HITL()

            # Manage threading
            self.automatic_mode.thread.terminate = False
            self.automatic_mode.thread.pause = False
            
            # Reset SimpleImageViewer widget
            self.automatic_mode.window.widget.reset()

            # Reset right widget
            self.automatic_mode.restart()

            # Reset left widget
            self.browse_mode.window.left_widget.model_file.show()
            self.browse_mode.window.left_widget.model_file_edit.show()
            self.browse_mode.window.left_widget.model_file_edit_text.show()
            
            # Pass loaded user data
            FilenamesGUI.copy(self.browse_mode.fname_images, self.automatic_mode.fname_images)
            FilenamesGUI.copy(self.browse_mode.fname_landmarks, self.automatic_mode.fname_landmarks)

        # If browse mode is selected, reset image and other relevant flags
        else:
            # Manage threading
            self.automatic_mode.thread.terminate = True
            
            # Reset SimpleImageViewer widget
            self.browse_mode.set_paths()
            self.browse_mode.load_img()
            self.browse_mode.window.widget.clear_3d()

            # Reset Left widget
            self.browse_mode.window.left_widget.model_file.hide()
            self.browse_mode.window.left_widget.model_file_edit.hide()
            self.browse_mode.window.left_widget.model_file_edit_text.hide()
            
            # Pass loaded user data
            FilenamesGUI.copy(self.automatic_mode.fname_images, self.browse_mode.fname_images)
            FilenamesGUI.copy(self.automatic_mode.fname_landmarks, self.browse_mode.fname_landmarks)
    
    def get_mode(self):
        """
        Used to find application mode (automatic or browse)
        """
        if self.tab_widget.currentIndex() == 0:
            return self.AUTOMATIC_MODE
        else:
            return self.BROWSE_MODE


################################################################################
## Main Function
# Responsible for execution of the whole application

if __name__ == "__main__":

    ########################################################################
    # PyQt GUI Code Section
    # Define application and viewer to run on the main thread
    controller = Controller()
    sys.exit(controller.app.exec_())

    ########################################################################

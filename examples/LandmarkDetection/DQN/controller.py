################################################################################
## Doorway to launch application's GUI
# Author: Maleakhi, Alex, Jamie, Faidon
################################################################################

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from RL.dataReader import *

from RL.DQN import get_viewer_data

def warn(*args, **kwargs):
    pass
import sys
import warnings
warnings.warn = warn
warnings.simplefilter("ignore", category=PendingDeprecationWarning)

from GUI.window import Window
from GUI.right_widget_automatic import RightWidgetSettings
from GUI.right_widget_browse import RightWidgetSettingsBrowseMode
from GUI.FilenamesGUI import FilenamesGUI


###############################################################################
## Controller class 
# Responsible to run the entire application

class Controller:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.viewer_param = get_viewer_data()
        self.testing = False

        # Initialise the right settings tab
        self.right_widget = Tab()

        # Initialise the window
        self.window = Window(self.viewer_param, self.right_widget)
        self.right_widget.automatic_mode.window = self.window
        self.right_widget.browse_mode.window = self.window
        
        # Show window
        self.window.show()

    @staticmethod
    def allWidgets_setCheckable(parentQWidget):
        ''' Method to set every widget to checkable for so the .isChecked()
            method can by used in testing.
        '''
        for topLevel in QApplication.topLevelWidgets():
            children = []
            for QObj in {QPushButton, QToolButton}:
                children.extend(topLevel.findChildren(QObj))
            for child in children:
                try:
                    child.setCheckable(True)
                except AttributeError:
                    pass


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

        self.testing = False
    
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
            self.browse_mode.window.left_widget.load_button.hide()
            self.browse_mode.window.left_widget.automatic_mode_help_text()
            
            # Pass loaded user data
            FilenamesGUI.copy(self.browse_mode.fname_images, self.automatic_mode.fname_images)
            FilenamesGUI.copy(self.browse_mode.fname_landmarks, self.automatic_mode.fname_landmarks)
            self.automatic_mode.terminal.appendHtml(f"<b><p style='color:blue'> &#36; Automatic Mode </p></b>")        
            self.automatic_mode.window.load_model_action.setEnabled(True)

        # If browse mode is selected, reset image and other relevant flags
        else:
            # Manage threading
            self.automatic_mode.thread.terminate = True
            
            # Reset SimpleImageViewer widget
            self.browse_mode.set_paths()
            self.browse_mode.load_img()
            self.browse_mode.window.widget.clear_3d()
            self.browse_mode.window.widget.set_3d_axes(self.browse_mode.window.widget.ax, \
                        self.browse_mode.window.widget.width, self.browse_mode.window.widget.height, \
                        self.browse_mode.window.widget.height_x)
            self.browse_mode.window.widget.canvas.draw()

            # Reset Left widget
            self.browse_mode.window.left_widget.model_file.hide()
            self.browse_mode.window.left_widget.model_file_edit.hide()
            self.browse_mode.window.left_widget.model_file_edit_text.hide()
            self.browse_mode.window.left_widget.load_button.show()
            self.browse_mode.window.left_widget.browse_mode_help_text()

            # Pass loaded user data
            FilenamesGUI.copy(self.automatic_mode.fname_images, self.browse_mode.fname_images)
            FilenamesGUI.copy(self.automatic_mode.fname_landmarks, self.browse_mode.fname_landmarks)
            self.browse_mode.terminal_duplicate.appendHtml(f"<b><p style='color:blue'> &#36; Browse Mode </p></b>")        
            self.browse_mode.window.load_model_action.setEnabled(False)

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

################################################################################
## Doorway to launch application's GUI
# Author: Maleakhi, Alex, Jamie, Faidon, Olle, Harry
################################################################################

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from RL.dataReader import *

from DQN import get_viewer_data

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
    """
    Class that initialise app object and run the entire application.
    """

    def __init__(self):

        # Initialise the application
        self.app = QApplication(sys.argv)
        self.viewer_param = get_viewer_data()
        self.testing = False
        self.app.setWindowIcon(QIcon('images/aladdin.png'))


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
        """
        Method to set every widget to checkable for so the .isChecked()
        method is used in testing.
        """

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
    """
    Class integrating automatic mode and browse mode settings.
    """

    # Constant indicating current mode
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

        # Manage responsive design
        self.setMaximumWidth(350)
        self.setStyleSheet("background:#EBEEEE")

        # Flag for unit testing
        self.testing = False
    
    def save_HITL(self):
        """
        Method to save HITL when appropriate. 
        """

        try:
            if self.browse_mode.env and self.browse_mode.HITL:
                self.browse_mode.save_HITL()
        except AttributeError:
            pass

    def setup_browse(self):
        """
        Reset and setup browse mode (useful for setup when tab changes).
        """

        # Reset data
        self.browse_mode.clear_custom_load()
        self.automatic_mode.clear_custom_load()
        self.browse_mode.window.left_widget.space.hide()
        self.browse_mode.window.load_model_action.setEnabled(False)

        # Manage thread flags
        self.automatic_mode.thread.terminate = True
            
        # Reset SimpleImageViewer widget (black image)
        self.browse_mode.set_paths()
        self.browse_mode.load_img()
        self.browse_mode.window.widget.plot_3d.clear_3d()
        self.browse_mode.window.widget.cnt_browse = 0

        # Reset right widget
        self.browse_mode.plot.clear_2d()

        # Reset left widget
        self.browse_mode.window.left_widget.model_file.hide()
        self.browse_mode.window.left_widget.model_file_edit.hide()
        self.browse_mode.window.left_widget.model_file_edit_text.hide()
        self.browse_mode.window.left_widget.load_button.show()
        self.browse_mode.window.left_widget.quick_help.browse_mode_help_text()
    
    def setup_automatic(self):
        """
        Reset and setup automatic mode (useful for setup when tab changes).
        """
        
        # Save HITL status
        self.save_HITL()

        # Reset data
        self.browse_mode.clear_custom_load()
        self.automatic_mode.clear_custom_load()
        self.automatic_mode.window.load_model_action.setEnabled(True)

        # Manage thread flags
        self.automatic_mode.thread.terminate = False
        self.automatic_mode.thread.pause = False
            
        # Reset SimpleImageViewer widget (black image)
        self.automatic_mode.window.widget.reset()

        # Reset right widget
        self.automatic_mode.restart()
        self.automatic_mode.terminal.add_log("blue", "Automatic Mode")       

        # Reset left widget
        self.automatic_mode.window.left_widget.model_file.show()
        self.automatic_mode.window.left_widget.model_file_edit.show()
        self.automatic_mode.window.left_widget.model_file_edit_text.show()
        self.automatic_mode.window.left_widget.load_button.hide()
        self.automatic_mode.window.left_widget.space.show()
        self.automatic_mode.window.left_widget.quick_help.automatic_mode_help_text()
    
    def on_change(self, index):
        """
        Event handler when tab changes
        """

        # If automatic mode is selected, reset image and other relevant flags
        if index == 0:
           self.setup_automatic()

        # If browse mode is selected, reset image and other relevant flags
        else:
            self.setup_browse()

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
    # Define application and viewer to run on the main thread
    controller = Controller()
    sys.exit(controller.app.exec_())

################################################################################
## Right widget files for browse mode
# Author: Maleakhi, Alex, Faidon, Jamie, Olle, Harry
################################################################################

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from RL.dataReader import *

from DQN import get_player

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn
warnings.simplefilter("ignore", category=PendingDeprecationWarning)

import numpy as np
import pickle
from datetime import datetime
import platform

from GUI.FilenamesGUI import FilenamesGUI
from GUI.plot import Plot
from GUI.window import Window


###############################################################################

# BATCH SIZE USED IN NATURE PAPER IS 32 - MEDICAL IS 256
BATCH_SIZE = 48
# BREAKOUT (84,84) - MEDICAL 2D (60,60) - MEDICAL 3D (26,26,26)
IMAGE_SIZE = (45, 45, 45)
# how many frames to keep
# in other words, how many observations the network can see
FRAME_HISTORY = 4
# the frequency of updating the target network
UPDATE_FREQ = 4
# DISCOUNT FACTOR - NATURE (0.99) - MEDICAL (0.9)
GAMMA = 0.9 #0.99
# REPLAY MEMORY SIZE - NATURE (1e6) - MEDICAL (1e5 view-patches)
MEMORY_SIZE = 1e5 #6
# consume at least 1e6 * 27 * 27 * 27 bytes
INIT_MEMORY_SIZE = MEMORY_SIZE // 20 #5e4
# each epoch is 100k played frames
STEPS_PER_EPOCH = 10000 // UPDATE_FREQ * 10
# num training epochs in between model evaluations
EPOCHS_PER_EVAL = 2
# the number of episodes to run during evaluation
EVAL_EPISODE = 50
        

###############################################################################
## Right Widget (Browse Mode)

class RightWidgetSettingsBrowseMode(QFrame):
    """
    Class representing right widget for browse mode.
    """

    def __init__(self, *args, **kwargs):

        super(RightWidgetSettingsBrowseMode, self).__init__(*args, **kwargs)
        self.window = None
        self.mounted = False

        ## Initialise widgets
        # Initialise widgets (HITL related)
        self.next_img = QPushButton('Next Image', self)
        self.HITL_mode = QCheckBox('Enable HITL', self)
        self.HITL_mode.setCheckable(True)
        self.HITL_delete = QPushButton('Delete Episode', self)
        self.HITL_delete.setDisabled(True)

        # Initialised widgets (movement widget)
        self.x_action = XMove(self)
        self.y_action = YMove(self)
        self.z_action = ZMove(self)

        # Set frame
        self.x_action.setFrameShape(QFrame.StyledPanel)
        self.y_action.setFrameShape(QFrame.StyledPanel)
        self.z_action.setFrameShape(QFrame.StyledPanel)

        # Zoom functionality
        self.zoomInButton = QToolButton(self)
        self.zoomInButton.setText('-')
        font = self.zoomInButton.font()
        font.setBold(True)
        self.zoomInButton.setFont(font)

        self.zoomOutButton = QToolButton(self)
        self.zoomOutButton.setText('+')
        font = self.zoomOutButton.font()
        font.setBold(True)
        self.zoomOutButton.setFont(font)

        # Error plot
        self.plot = Plot()

        # Placeholder for GUI filenames
        self.fname_images = FilenamesGUI()
        self.fname_landmarks = FilenamesGUI()

        ## Initialise layout
        # Widget for move actions
        hbox_action = QHBoxLayout()
        hbox_action.addWidget(self.x_action)
        hbox_action.addWidget(self.y_action)
        hbox_action.addWidget(self.z_action)
        hbox_action.addStretch()

        # Widget zoom in and zoom out
        hbox_zoom = QHBoxLayout()
        hbox_zoom.addWidget(self.zoomInButton)
        hbox_zoom.addWidget(self.zoomOutButton)
        hbox_zoom.addStretch()

        # Widget for Next image and Delete Episode
        hbox_image = QHBoxLayout()
        hbox_image.setSpacing(30)
        hbox_image.addWidget(self.next_img)
        hbox_image.addWidget(self.HITL_delete)

        vbox = QVBoxLayout()
        vbox.setSpacing(20)
        vbox.addWidget(QLabel("Human Actions"))
        vbox.addLayout(hbox_action)
        vbox.addWidget(QLabel("<hr />"))
        vbox.addWidget(QLabel("Step Size Magnification"))
        vbox.addLayout(hbox_zoom)
        vbox.addWidget(QLabel("<hr />"))
        vbox.addWidget(QLabel("HITL Settings"))
        vbox.addItem(QSpacerItem(0,10))
        vbox.addWidget(self.HITL_mode)
        vbox.addItem(QSpacerItem(0,20))
        vbox.addLayout(hbox_image)
        vbox.addWidget(self.plot)
        vbox.addStretch()

        self.setLayout(vbox)

        # Connections
        self.HITL_mode.clicked.connect(self.on_clicking_HITL)
        self.next_img.clicked.connect(self.on_clicking_nextImg)
        self.HITL_delete.clicked.connect(self.on_clicking_HITLDelete)
        self.zoomOutButton.clicked.connect(self.on_clicking_zoomOut)
        self.zoomInButton.clicked.connect(self.on_clicking_zoomIn)

        # CSS styling
        self.zoomOutButton.setStyleSheet("background: white; color: black; border:none;")
        self.zoomInButton.setStyleSheet("background: white; color: black; border: none")
        with open ("GUI/css/right_widget_browse.css", "r") as f:
            self.setStyleSheet(f.read())
        self.next_img.setStyleSheet("background: orange; color:white")
        
        # Indicate unit testing mode
        self.testing = False

        # HITL related variable
        self.env = None
        self.HITL = False
        self.HITL_logger = []

    def on_clicking_nextImg(self):
        """
        Event handler for clicking next image
        """

        self.env.reset()
        
        # Reset 2d and 3d plot
        self.window.widget.plot_3d.clear_3d()
        self.plot.clear_2d()
        self.window.widget.cnt_browse = 0
        
        self.move_img(-1)

        # If doing HITL, 50/50 chance for the resultion to start on 2 or 3 
        # (otherwise resolution=2 tends to get negleted)
        if self.HITL and np.random.choice(2):
            self.on_clicking_zoomIn()

    def on_clicking_HITL(self):
        """ 
        Activating HITL mode gives following actions:
        - Make HITL_delete button clickable
        - Make HITL_mode button clickable

        Deactivating HITL mode gives following actions:
        - Save HITL episode
        - Make HITL delete button un-clickable
        - Un-click HITL mode check box
        """

        if self.testing:
            result = QMessageBox.Yes
        else:
            result = self.show_HITL_msg()

        if result == QMessageBox.Yes and self.HITL:
            self.save_HITL()

        if result == QMessageBox.Yes and not self.HITL:
            # Activate HITL mode button
            self.HITL_mode.setChecked(True)
            self.HITL_delete.setDisabled(False)

        elif result == QMessageBox.No and self.HITL:
            self.HITL_mode.setChecked(True)

        elif (result == QMessageBox.No and not self.HITL) or \
            (result == QMessageBox.Yes and self.HITL):
            self.HITL_mode.setChecked(False)
            self.HITL_delete.setDisabled(True)

        if result == QMessageBox.Yes:
            self.HITL = not self.HITL
            self.env.HITL_logger.clear()

    def on_clicking_HITLDelete(self):
        """
        Helper function to remove lates HITL episode.
        """

        if self.testing:
            result = QMessageBox.Yes
        else:
            result = self.show_HITL_del_msg()

        # Remove the current episode and load a new image
        if result == QMessageBox.Yes:
            self.on_clicking_nextImg()
            self.env.HITL_logger.pop()

    def on_clicking_zoomIn(self):
        """
        Event handler for zoom in.
        """

        if self.env and self.env.xscale > 1:
            self.env.adjustMultiScale(higherRes=True)
            self.move_img(-1)

    def on_clicking_zoomOut(self):
        """
        Event handler for zoom out.
        """

        if self.env and self.env.xscale < 3:
            self.env.adjustMultiScale(higherRes=False)
            self.move_img(-1)

    def load_img(self):
        """
        Load appropriate image to display on viewer object.
        """
        try:
            self.selected_list = [self.fname_images, self.fname_landmarks]
            self.env = get_player(files_list=self.selected_list, viz=0.01,
                             saveGif=False, saveVideo=False, task='browse',
                            data_type=self.window.usecase)
        
            self.env.stepManual(act=-1, viewer=self.window)
            self.env.display()
        except:
            # Warn user about error, set default data, load default data
            self.error_message_box()
            self.set_paths()
    
    def clear_custom_load(self):
        """
        Clear user load custom data.
        """

        self.fname_images.clear()
        self.fname_landmarks.clear()

        self.window.left_widget.reset_file_edit_text()

    def move_img(self, action):
        """
        Move image after user pressed an action.

        :param action: integer representing user action choice.
        """

        self.env.stepManual(action, self.window)
        QApplication.processEvents()
        self.window.update()
    
    def set_paths(self):
        self.window.usecase = self.which_usecase()
        redir = '' if self.mounted else 'local/'

        if self.window.usecase == Window.BRAIN:
            # Default MRI
            self.fname_images.name = f"./data/filenames/{redir}brain_train_files_new_paths.txt"
            self.fname_landmarks.name = f"./data/filenames/{redir}brain_train_landmarks_new_paths.txt"
            self.window.widget.change_layout(self.window.usecase)
        elif self.window.usecase == Window.CARDIAC:
            # Default cardiac
            self.fname_images.name = f"./data/filenames/{redir}cardiac_train_files_new_paths.txt"
            self.fname_landmarks.name = f"./data/filenames/{redir}cardiac_train_landmarks_new_paths.txt"
            self.window.widget.change_layout(self.window.usecase)
        elif self.window.usecase == Window.FETAL:
            # Default fetal
            self.fname_images.name = f"./data/filenames/{redir}fetalUS_train_files_new_paths.txt"
            self.fname_landmarks.name = f"./data/filenames/{redir}fetalUS_train_landmarks_new_paths.txt"
            self.window.widget.change_layout(self.window.usecase)
        else:
            # User defined file selection
            self.fname_images.name = self.window.left_widget.fname_images
            self.fname_landmarks.name = self.window.left_widget.fname_landmarks

            # To tell the program which loader it should use
            self.window.usecase = self.check_user_define_usecase(self.fname_images.name, self.fname_landmarks.name)

            # If usecase is still user defined
            if self.window.usecase == Window.USER_DEFINED:
                self.error_message_box()
                self.set_paths() # Set default path again
            else:
                self.window.widget.change_layout(self.window.usecase)
    
    def check_user_define_usecase(self, filename_img, filename_landmark):
        """
        Check which usecase that the user wants (in case of custom data loaded by user)

        :param filename_img: string representing file name for image
        :param filename_landmark: string representing file name for landmark
        """

        filename_img = filename_img.split("/")
        filename_landmark = filename_landmark.split("/")

        # Ensure that user input file properly
        if "cardiac" in filename_img[-1]\
            and "cardiac" in filename_landmark[-1] :
            return Window.CARDIAC
        elif "brain" in filename_img[-1] \
            and "brain" in filename_landmark[-1]:
            return Window.BRAIN
        elif "fetal" in filename_img[-1] \
            and "fetal" in filename_landmark[-1]:
            return Window.FETAL
        else:
            return Window.USER_DEFINED
    
    def error_message_box(self):
        """
        Error message if user incorrectly upload file
        """

        msg = QMessageBox()
        msg.setWindowTitle("Error on user defined settings")
        msg.setText("Please use appropriate model, image, and landmarks.")
        msg.setIcon(QMessageBox.Critical)

        # Clean up
        self.clear_custom_load()
        self.window.usecase = self.which_usecase()

        # Display pop up message
        msg.exec_()
    
    def which_usecase(self):
        """
        Determine which radio button usecase is checked.
        """

        # If user does not specify specific file to load
        if not self.fname_images.user_define or \
            not self.fname_landmarks.user_define:
            if self.window.left_widget.brain_button.isChecked():
                return Window.BRAIN
            elif self.window.left_widget.cardiac_button.isChecked():
                return Window.CARDIAC
            else:
                return Window.FETAL

        # Else user specify
        else:
            return Window.USER_DEFINED

    def show_HITL_msg(self):
        """
        Generate HITL warning message when clicked. (HITL mode)
        """

        self.HITL_msg = QMessageBox()
        self.HITL_msg.setIcon(QMessageBox.Question)
        if not self.HITL:
            self.HITL_msg.setText("Human-In-The-Loop mode enabled")
            self.HITL_msg.setInformativeText(("In Human-In-The-Loop mode, your "
                "interactions will now be saved and used to train the reinforcement "
                "learning algorithm faster. \n Do you want to proceed?"))
        else:
            self.HITL_msg.setText("Human-In-The-Loop mode disabled")
            self.HITL_msg.setInformativeText(("Human-In-The-Loop mode "
                "will now be disabled. \n Do you want to proceed?"))
        self.HITL_msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.HITL_msg.setDefaultButton(QMessageBox.Yes)
        result = self.HITL_msg.exec_()
        return result

    def show_HITL_del_msg(self):
        """
        Generate HITL warning message when clicked. (episode deletion)
        """

        self.HITL_del_msg = QMessageBox()
        self.HITL_del_msg.setIcon(QMessageBox.Warning)
        self.HITL_del_msg.setText("Delete button clicked")
        self.HITL_del_msg.setInformativeText(("\n This will delete the current "
            "episode. \nDo you want to proceed?"))
        self.HITL_del_msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.HITL_del_msg.setDefaultButton(QMessageBox.Yes)
        result = self.HITL_del_msg.exec_()
        return result

    def save_HITL(self):
        """
        Save HITL pickle file.
        """

        # Record current HITL loop
        if len(self.env._loc_history) > 1:
            self.env.reset()

        # Create pickle file
        now = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        device_name = platform.node()
        path = f'./data/HITL/log_{self.window.usecase}_{str(now)}_{device_name}.pickle'
        with open(path, 'wb') as f:
            pickle.dump(self.env.HITL_logger, f)
        

###############################################################################
##  X, Y, Z Sub-Widgets
# Used for agent action

class YMove(QFrame):
    """
    Class widget for Y axis movement.
    """

    def __init__(self, right_widget):

        super().__init__()
        self.right_widget = right_widget # pointer to parent

        # Initialise button
        self.label = QLabel("<i> Y </i>")
        self.up_button = QToolButton(self)
        self.up_button.setArrowType(Qt.UpArrow)

        self.down_button = QToolButton(self)
        self.down_button.setArrowType(Qt.DownArrow)

        # Setup layout
        vbox = QVBoxLayout()
        vbox.setSpacing(10)
        vbox.addWidget(self.label)
        vbox.addWidget(self.up_button)
        vbox.addWidget(self.down_button)

        self.setLayout(vbox)

        # Connection
        self.up_button.clicked.connect(self.on_clicking_up)
        self.down_button.clicked.connect(self.on_clicking_down)

        # CSS Styling
        self.label.setAlignment(Qt.AlignCenter)
        vbox.setAlignment(Qt.AlignCenter)
        self.setMaximumWidth(50)
        self.label.setStyleSheet("border:None")

    def on_clicking_up(self):
        """
        Event handler when up arrow or keyboard shortcut is pressed.
        """

        if self.right_widget.env:
            # Adjust keybindings to acccount for rotation of fetal images
            if self.right_widget.window.usecase == Window.FETAL:
                action = 3
            else:
                action = 1 
            self.right_widget.move_img(action)

    def on_clicking_down(self):
        """
        Event handler when down arrow or keyboard shortcut is pressed.
        """

        if self.right_widget.env:
            # Adjust keybindings to acccount for rotation of fetal images
            if self.right_widget.window.usecase == Window.FETAL:
                action = 2
            else:
                action = 4
            self.right_widget.move_img(action)


class XMove(QFrame):
    """
    Class widget for X axis movement.
    """

    def __init__(self, right_widget):

        super().__init__()
        self.right_widget = right_widget # pointer to parent

        # Initialise button
        self.label = QLabel("<i> X </i>")
        self.left_button = QToolButton(self)
        self.left_button.setArrowType(Qt.LeftArrow)

        self.right_button = QToolButton(self)
        self.right_button.setArrowType(Qt.RightArrow)

        # Setup layout
        vbox = QVBoxLayout()
        vbox.setSpacing(10)
        vbox.addWidget(self.label)
        vbox.addWidget(self.right_button)
        vbox.addWidget(self.left_button)

        self.setLayout(vbox)

        # Connection
        self.left_button.clicked.connect(self.on_clicking_left)
        self.right_button.clicked.connect(self.on_clicking_right)

        # CSS Styling
        self.label.setAlignment(Qt.AlignCenter)
        vbox.setAlignment(Qt.AlignCenter)
        self.setMaximumWidth(50)
        self.label.setStyleSheet("border:None")

    def on_clicking_left(self):
        """
        Event handler when left arrow or keyboard shortcut is pressed.
        """

        if self.right_widget.env:
            # Adjust keybindings to acccount for rotation of fetal images
            if self.right_widget.window.usecase == Window.FETAL:
                action = 4
            else:
                action = 3
            self.right_widget.move_img(action)

    def on_clicking_right(self):
        """
        Event handler when right arrow or keyboard shortcut is pressed.
        """

        if self.right_widget.env:
            # Adjust keybindings to acccount for rotation of fetal images
            if self.right_widget.window.usecase == Window.FETAL:
                action = 1
            else:
                action = 2
            self.right_widget.move_img(action)


class ZMove(QFrame):
    """
    Class widget for Z axis movement.
    """

    def __init__(self, right_widget):

        super().__init__()
        self.right_widget = right_widget # pointer to parent

        # Initialise button
        self.label = QLabel("<i> Z </i>")
        self.in_button = QToolButton(self)
        self.in_button.setArrowType(Qt.UpArrow)

        self.out_button = QToolButton(self)
        self.out_button.setArrowType(Qt.DownArrow)

        # Setup layout
        vbox = QVBoxLayout()
        vbox.setSpacing(10)
        vbox.addWidget(self.label)
        vbox.addWidget(self.in_button)
        vbox.addWidget(self.out_button)
        # vbox.setAlignment(Qt.AlignCenter)

        self.setLayout(vbox)

        # Connection
        self.in_button.clicked.connect(self.on_clicking_in)
        self.out_button.clicked.connect(self.on_clicking_out)

        # CSS Styling
        self.label.setAlignment(Qt.AlignCenter)
        vbox.setAlignment(Qt.AlignCenter)
        self.setMaximumWidth(50)
        self.label.setStyleSheet("border:None")

    def on_clicking_in(self):
        """
        Event handler to go in the Z direction.
        """

        if self.right_widget.env:
            action = 0
            self.right_widget.move_img(action)

    def on_clicking_out(self):
        """
        Event handler to go in the Z direction.
        """

        if self.right_widget.env:
            action = 5
            self.right_widget.move_img(action)

        

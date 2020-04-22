################################################################################
## Right widget files for browse mode
# Author: Maleakhi, Alex, Faidon, Jamie
################################################################################

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from dataReader import *

from DQN import get_player

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn
warnings.simplefilter("ignore", category=PendingDeprecationWarning)

import numpy as np
import pickle
from thread import WorkerThread
from datetime import datetime
import platform

from FilenamesGUI import FilenamesGUI


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
##  Sub-Widgets
# Used for agent action

class XMove(QFrame):

    def __init__(self, right_widget):
        super().__init__()
        self.right_widget = right_widget # pointer to parent

        # Initialise button
        self.label = QLabel("X")
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

    @pyqtSlot()
    def on_clicking_up(self):
        if self.right_widget.env:
            action = 1 if self.right_widget.window.usecase != 'FetalUS' else 3
            self.right_widget.move_img(action)

    @pyqtSlot()
    def on_clicking_down(self):
        if self.right_widget.env:
            action = 4 if self.right_widget.window.usecase != 'FetalUS' else 2
            self.right_widget.move_img(action)


class YMove(QFrame):

    def __init__(self, right_widget):
        super().__init__()
        self.right_widget = right_widget # pointer to parent

        # Initialise button
        self.label = QLabel("Y")
        self.left_button = QToolButton(self)
        self.left_button.setArrowType(Qt.DownArrow)

        self.right_button = QToolButton(self)
        self.right_button.setArrowType(Qt.UpArrow)

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


    @pyqtSlot()
    def on_clicking_left(self):
        if self.right_widget.env:
            action = 3 if self.right_widget.window.usecase != 'FetalUS' else 4
            self.right_widget.move_img(action)

    @pyqtSlot()
    def on_clicking_right(self):
        if self.right_widget.env:
            action = 2 if self.right_widget.window.usecase != 'FetalUS' else 1
            self.right_widget.move_img(action)


class ZMove(QFrame):

    def __init__(self, right_widget):
        super().__init__()
        self.right_widget = right_widget # pointer to parent

        # Initialise button
        self.label = QLabel("Z")
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

    @pyqtSlot()
    def on_clicking_in(self):
        if self.right_widget.env:
            action = 0
            self.right_widget.move_img(action)

    @pyqtSlot()
    def on_clicking_out(self):
        if self.right_widget.env:
            action = 5
            self.right_widget.move_img(action)
        

###############################################################################
## Right Widget (Browse Mode)

class RightWidgetSettingsBrowseMode(QFrame):

    def __init__(self, *args, **kwargs):
        super(RightWidgetSettingsBrowseMode, self).__init__(*args, **kwargs)
        # Window and thread object
        self.window = None
        self.thread = WorkerThread(None)
        self.thread.pause = False
        
        # Mounting by default is false
        self.mounted = False

        # Initialise widgets (HITL related)
        self.next_img = QPushButton('Next Image', self)
        self.HITL_mode = QCheckBox('Enable HITL',self)
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
        self.zoomInButton.setText('+')
        font = self.zoomInButton.font()
        font.setBold(True)
        self.zoomInButton.setFont(font)

        self.zoomOutButton = QToolButton(self)
        self.zoomOutButton.setText('-')
        font = self.zoomOutButton.font()
        font.setBold(True)
        self.zoomOutButton.setFont(font)

        # Placeholder for GUI filenames
        self.fname_images = FilenamesGUI()
        self.fname_landmarks = FilenamesGUI()

        ## Initialise layout
        # Widget for move actions
        hbox_action = QHBoxLayout()
        hbox_action.addWidget(self.x_action)
        hbox_action.addWidget(self.y_action)
        hbox_action.addWidget(self.z_action)

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
        vbox.addWidget(QLabel("<i> Agent Actions </i>"))
        vbox.addLayout(hbox_action)
        vbox.addWidget(QLabel("<hr />"))
        vbox.addWidget(QLabel("<i> Step Size Magnification </i>"))
        vbox.addLayout(hbox_zoom)
        vbox.addWidget(QLabel("<hr />"))
        vbox.addWidget(QLabel("<i> Human-in-the-loop Settings </i>"))
        vbox.addItem(QSpacerItem(0,10))
        vbox.addWidget(self.HITL_mode)
        vbox.addItem(QSpacerItem(0,20))
        vbox.addLayout(hbox_image)
        vbox.addStretch()

        self.setLayout(vbox)

        # Connections
        self.HITL_mode.clicked.connect(self.on_clicking_HITL)
        self.next_img.clicked.connect(self.on_clicking_nextImg)
        self.HITL_delete.clicked.connect(self.on_clicking_HITLDelete)
        self.zoomOutButton.clicked.connect(self.on_clicking_zoomOut)
        self.zoomInButton.clicked.connect(self.on_clicking_zoomIn)

        # CSS
        self.zoomOutButton.setStyleSheet("background: white; color: black; border:none;")
        self.zoomInButton.setStyleSheet("background: white; color: black; border: none")
        self.setStyleSheet("""
            QPushButton:disabled {
                background: white;
                color: grey;
            }

            QPushButton{
                background: #f44336;
                color: white;
            }

            QFrame {
                background: white;
            }

            QCheckBox{
                background: white
            }
        """)

        self.next_img.setStyleSheet("background: orange; color:white")
        self.x_action.setStyleSheet("""
        QFrame {
            border:2px solid #DD2501
        }

        QToolButton {
            background: white;
            border: none;
            color: black !important;
        }
        """)
        self.y_action.setStyleSheet("""
        QFrame {border:2px solid #66A40A}
        QToolButton {
            background: white;
            border: none;
            color: black !important;
        }
        """)
        self.z_action.setStyleSheet("""
        QFrame {border:2px solid #006EAF}
        QToolButton {
            background: white;
            border: none;
            color: black !important;
        }
        """)
        
        # HITL related variable
        self.testing = False
        self.env = None
        self.HITL = False
        self.HITL_logger = []

    @pyqtSlot()
    def on_clicking_nextImg(self):
        self.env.reset()
        self.move_img(-1)

        # If doing HITL, 50/50 chance for the resultion to start on 2 or 3 (otherwise resolution=2 tends to get negleted)
        if self.HITL and np.random.choice(2):
            self.on_clicking_zoomIn()

    @pyqtSlot()
    def on_clicking_HITL(self):
        ''' Activating HITL mode giv es following actions:
            - Make HITL_delete button clickable
            - Make HITL_mode button clickable

            Deactivating HITL mode gives following actions:
            - Save HITL episode
            - Make HITL delete button un-clickable
            - Un-click HITL mode check box
        '''
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

    @pyqtSlot()
    def on_clicking_HITLDelete(self):
        if self.testing:
            result = QMessageBox.Yes
        else:
            result = self.show_HITL_del_msg()

        # Remove the current episode and load a new image
        if result == QMessageBox.Yes:
            self.on_clicking_nextImg()
            self.env.HITL_logger.pop()

    @pyqtSlot()
    def on_clicking_zoomIn(self):
        if self.env and self.env.xscale > 1:
            self.env.adjustMultiScale(higherRes=True)
            self.move_img(-1)

    @pyqtSlot()
    def on_clicking_zoomOut(self):
        if self.env and self.env.xscale < 3:
            self.env.adjustMultiScale(higherRes=False)
            self.move_img(-1)

    def load_img(self):
        self.selected_list = [self.fname_images, self.fname_landmarks]
        self.env = get_player(files_list=self.selected_list, viz=0.01,
                             saveGif=False, saveVideo=False, task='browse',
                            data_type=self.default_use_case)
        
        self.env.stepManual(act=-1, viewer=self.window)
        self.env.display()

    def move_img(self, action):
        self.env.stepManual(action, self.window)
        QApplication.processEvents()
        self.window.update()
    
    def set_paths(self):
        self.default_use_case = self.which_usecase()

        redir = '' if self.mounted else 'local/'

        if self.default_use_case == 'BrainMRI':
            # Default MRI
            self.fname_images.name = f"./data/filenames/{redir}brain_train_files_new_paths.txt"
            self.fname_landmarks.name = f"./data/filenames/{redir}brain_train_landmarks_new_paths.txt"
        elif self.default_use_case == 'CardiacMRI':
            # Default cardiac
            self.fname_images.name = f"./data/filenames/{redir}cardiac_train_files_new_paths.txt"
            self.fname_landmarks.name = f"./data/filenames/{redir}cardiac_train_landmarks_new_paths.txt"
        elif self.default_use_case == 'FetalUS':
            # Default fetal
            self.fname_images.name = f"./data/filenames/{redir}fetalUS_train_files_new_paths.txt"
            self.fname_landmarks.name = f"./data/filenames/{redir}fetalUS_train_landmarks_new_paths.txt"
        else:
            # User defined file selection
            self.fname_images.name = self.window.left_widget.fname_images
            self.fname_landmarks.name = self.window.left_widget.fname_landmarks

            # To tell the program which loader it should use
            self.default_use_case = self.check_user_define_usecase(self.fname_images.name, self.fname_landmarks.name)

            # If usecase is wrong
            if not self.default_use_case:
                self.error_message_box()
                self.default_use_case = self.which_usecase()

        self.window.usecase = self.default_use_case # indicate which use case currently
    
    def check_user_define_usecase(self, filename_img, filename_landmark):
        """
        Check which usecase that the user wants
        """
        filename_img = filename_img.split("/")
        filename_landmark = filename_landmark.split("/")

        # Ensure that user input file properly
        if "cardiac" in filename_img[-1]\
            and "cardiac" in filename_landmark[-1] :
            return "CardiacMRI"
        elif "brain" in filename_img[-1] \
            and "brain" in filename_landmark[-1]:
            return "BrainMRI"
        elif "fetal" in filename_img[-1] \
            and "fetal" in filename_landmark[-1]:
            return "FetalUS"
        else:
            return ""
    
    def error_message_box(self):
        """
        Error message if user incorrectly upload file
        """
        msg = QMessageBox()
        msg.setWindowTitle("Error on user defined settings")
        msg.setText("Please use appropriate model, image, and landmarks.")
        msg.setIcon(QMessageBox.Critical)

        # Clean up
        self.fname_landmarks.user_define = False
        self.fname_images.user_define = False

        self.window.left_widget.reset_file_edit_text()
        
        # Display pop up message
        msg.exec_()
    
    def which_usecase(self):
        """
        Determine which radio button usecase is checked
        """
        # If user does not specify specific file to load
        if not self.fname_images.user_define or \
            not self.fname_landmarks.user_define:
            if self.window.left_widget.brain_button.isChecked():
                return "BrainMRI"
            elif self.window.left_widget.cardiac_button.isChecked():
                return "CardiacMRI"
            else:
                return "FetalUS"
        # Else user specify
        else:
            return ""

    def show_HITL_msg(self):
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
        # Record current HITL loop
        if len(self.env._loc_history) > 1:
            self.env.reset()

        # Create pickle file
        now = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        device_name = platform.node()
        path = f'./data/HITL/log_{self.window.usecase}_{str(now)}_{device_name}.pickle'
        with open(path, 'wb') as f:
            pickle.dump(self.env.HITL_logger, f)
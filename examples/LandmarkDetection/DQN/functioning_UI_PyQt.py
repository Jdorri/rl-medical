################################################################################
## Doorway to launch application's GUI
# Author: Jamie, Faidon, Alex, Maleakhi
################################################################################

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from dataReader import *

from DQN import get_player, Model, get_config, get_viewer_data

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn
warnings.simplefilter("ignore", category=PendingDeprecationWarning)

import numpy as np

import os
import sys
import time
import argparse
from collections import deque

import tensorflow as tf
from medical import MedicalPlayer, FrameStack
from tensorpack.input_source import QueueInput
from tensorpack_medical.models.conv3d import Conv3D
from tensorpack_medical.models.pool3d import MaxPooling3D
from common import Evaluator, eval_model_multithread, play_n_episodes
from DQNModel import Model3D as DQNModel
from expreplay import ExpReplay

from tensorpack import (PredictConfig, OfflinePredictor, get_model_loader,
                        logger, TrainConfig, ModelSaver, PeriodicTrigger,
                        ScheduledHyperParamSetter, ObjAttrParam,
                        HumanHyperParamSetter, argscope, RunOp, LinearWrap,
                        FullyConnected, PReLU, SimpleTrainer,
                        launch_train_with_config)

from viewer import SimpleImageViewer, Window
import pickle
from thread import WorkerThread

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
## Controller class 
# Responsible to run the entire application

class Controller:
    def __init__(self, display=True):
        self.window = None # Application window
        self.app = QApplication(sys.argv)
        self.viewer_param = get_viewer_data()

        # Initialise the right settings tab
        self.right_settings = Tab()

        # Initialise the window
        self.window = Window(self.viewer_param, self.right_settings)
        self.right_settings.automatic_mode.window = self.window
        self.right_settings.browse_mode.window = self.window
        
        # # Set paths and load image
        # self.right_settings.browse_mode.set_paths()
        # self.right_settings.browse_mode.load_img()

        # Show window
        self.window.show()


###############################################################################
## Tab Widget
# Responsible to integrate automatic mode and browse mode through tab functionality

class Tab(QFrame):
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
    
    @pyqtSlot(int)
    def on_change(self, index):
        # If automatic mode is selected, reset image and other relevant flags
        if index == 0:
            self.automatic_mode.thread.terminate = False
            self.automatic_mode.thread.pause = False
            self.automatic_mode.window.widget.reset()
            self.automatic_mode.run_button.setStyleSheet("background-color:#4CAF50; color:white")
            self.automatic_mode.run_button.setText("Start")
            self.browse_mode.window.left_widget.model_file.show()
            self.browse_mode.window.left_widget.model_file_edit.show()
            self.browse_mode.window.left_widget.model_file_edit_text.show()
            
            # Pass the data
            filenames_GUI.copy(self.browse_mode.fname_images, self.automatic_mode.fname_images)
            filenames_GUI.copy(self.browse_mode.fname_landmarks, self.automatic_mode.fname_landmarks)

        # If browse mode is selected, reset image and other relevant flags
        else:
            self.automatic_mode.thread.terminate = True
            self.browse_mode.set_paths()
            self.browse_mode.load_img()
            self.browse_mode.window.left_widget.model_file.hide()
            self.browse_mode.window.left_widget.model_file_edit.hide()
            self.browse_mode.window.left_widget.model_file_edit_text.hide()

            # Pass data
            filenames_GUI.copy(self.automatic_mode.fname_images, self.browse_mode.fname_images)
            filenames_GUI.copy(self.automatic_mode.fname_landmarks, self.browse_mode.fname_landmarks)
    
    def get_mode(self):
        """
        Used to find application mode (automatic or browse)
        """
        if self.tab_widget.currentIndex() == 0:
            return "AUTOMATIC"
        else:
            return "BROWSE"


###############################################################################
## Right Widget (Automatic Mode)

class filenames_GUI:
    def __init__(self):
        self.user_define = False
        self.name = ""
    
    @staticmethod
    def copy(file1, file2):
        """
        Copy file 1 to file 2
        """
        file2.name = file1.name
        file2.user_define = file1.user_define

class RightWidgetSettings(QFrame):
    terminal_signal = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super(RightWidgetSettings, self).__init__(*args, **kwargs)
        # Responsive settings
        # self.setMaximumWidth(400)

        # Thread and window object which will be used to gain access to primary
        # windows.
        self.thread = WorkerThread(None)
        self.window = None

        # Placeholder for GUI file names, status
        self.fname_images = filenames_GUI()
        self.fname_landmarks = filenames_GUI()
        self.fname_model = filenames_GUI()

        # Task
        self.task = QLabel('<i> Task </i>', self)
        self.play_button = QRadioButton("Play")
        self.play_button.setChecked(True)
        self.eval_button = QRadioButton("Evaluation")

        # Agent speed
        label_speed = QLabel("<i> Agent Speed </i>")
        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(5)
        self.speed_slider.setValue(5)
        self.speed_slider.valueChanged[int].connect(self.changeValue)

        # Run and terminate
        self.run_button = QPushButton('Start', self)
        self.terminate_button = QPushButton('Terminate', self)

        # Terminal log
        label_log = QLabel("Logs")
        label_log.setStyleSheet("margin-top: 10px")
        self.terminal = QPlainTextEdit(self)
        self.terminal.setReadOnly(True)

        ## Layout
        # Task layout
        hbox_task = QHBoxLayout()
        hbox_task.setSpacing(30)
        hbox_task.addWidget(self.play_button)
        hbox_task.addWidget(self.eval_button)

        # Run layout
        hbox_run = QHBoxLayout()
        hbox_run.setSpacing(30)
        hbox_run.addWidget(self.run_button)
        hbox_run.addWidget(self.terminate_button)

        # Task, agent speed, run, layout
        grid = QGridLayout()
        grid.setVerticalSpacing(20) # spacing
        grid.addWidget(self.task, 1, 0)
        grid.addLayout(hbox_task, 2, 0)
        grid.addWidget(QLabel("<hr />"), 3, 0, 1, 2)
        grid.addWidget(label_speed, 4, 0, 1, 2)
        grid.addWidget(self.speed_slider, 5, 0, 1, 2)
        grid.addItem(QSpacerItem(0, 50), 6, 0) # add space
        grid.addLayout(hbox_run, 7, 0)

        # Main layout
        vbox = QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addItem(QSpacerItem(300, 50)) # spacer
        vbox.addWidget(label_log)
        vbox.addWidget(self.terminal)
        vbox.addStretch()

        self.setLayout(vbox)

        # Event handler
        self.run_button.clicked.connect(self.on_clicking_run)
        self.terminal_signal.connect(self.terminal_signal_handler)
        self.terminate_button.clicked.connect(self.on_clicking_terminate)
        
        # CSS styling for some widget components
        self.setStyleSheet("background:white")
        self.run_button.setStyleSheet("background-color:#4CAF50; color:white")
        self.terminate_button.setStyleSheet("background-color:#f44336; color:white")

        self.show()
    
    @pyqtSlot(int)
    def changeValue(self, value):
        """
        Event handler for slider (adjusting agent speed)
        """
        if value >= 4:
            self.thread.speed = WorkerThread.FAST
        elif value >= 2:
            self.thread.speed = WorkerThread.MEDIUM
        else:
            self.thread.speed = WorkerThread.SLOW
    
    @pyqtSlot()
    def on_clicking_terminate(self):
        self.thread.terminate = True # give signal to terminate thread
        self.thread.pause = False
        self.terminal.appendHtml(f"<b><p style='color:blue'> &#36; Terminate </p></b>")
        self.run_button.setText("Start")
        self.run_button.setStyleSheet("background-color:#4CAF50; color:white")
        
        # Reset simple image viewer
        self.window.widget.reset()

        self.window.statusbar.showMessage("Ready")
    
    def which_task(self):
        """
        Determine which radio button task is checked
        """
        if self.play_button.isChecked():
            return "Play"
        else:
            return "Evaluation"
    
    def which_usecase(self):
        """
        Determine which radio button usecase is checked
        """
        # If user does not specify specific file to load
        if not self.fname_images.user_define or \
            not self.fname_landmarks.user_define or \
                not self.fname_model.user_define:
            if self.window.left_widget.brain_button.isChecked():
                return "BrainMRI"
            elif self.window.left_widget.cardiac_button.isChecked():
                return "CardiacMRI"
            else:
                return "FetalUS"
        # Else user specify
        else:
            return "UserDefined"

    @pyqtSlot()
    def on_clicking_run(self):
        """
        Event handler (slot) for when the button is clicked
        """
        if self.run_button.text() == "Start":
            self.thread.terminate = False
            self.task_value = self.which_task()
            self.GIF_value = False
            self.video_value = False
            self.run_button.setText("Pause")
            self.window.statusbar.showMessage("Running")
            self.run_button.setStyleSheet("background-color:orange; color:white")
            self.default_use_case = self.which_usecase()
            self.set_paths(self.default_use_case)
            self.terminal.appendHtml(f"<b><p style='color:blue'> &#36; Start {self.task_value} Mode ({self.default_use_case}) </p></b>")
            self.run_DQN()
        elif self.run_button.text() == "Resume":
            self.thread.pause = False
            self.run_button.setText("Pause")
            self.terminal.appendHtml(f"<b><p style='color:blue'> &#36; Resume </p></b>")
            self.run_button.setStyleSheet("background-color:orange; color:white")
            self.window.statusbar.showMessage("Running")
        else:
            self.thread.pause = True
            self.run_button.setText("Resume")
            self.run_button.setStyleSheet("background-color:#4CAF50; color:white")
            self.terminal.appendHtml(f"<b><p style='color:blue'> &#36; Pause </p></b>")
            self.window.statusbar.showMessage("Paused")

    @pyqtSlot(dict)
    def terminal_signal_handler(self, value):
        """
        Used to handle agent signal when it moves.
        """
        current_episode = value["current_episode"]
        total_episode = value["total_episode"]
        score = value["score"]
        distance_error = value["distance_error"]
        q_values = value["q_values"]

        self.terminal.appendHtml(
            f"<b> Episode {current_episode}/{total_episode} </b>"
        )

        self.terminal.appendHtml(
            f"<i>Score:</i> {score}"
        )

        self.terminal.appendHtml(
            f"<i>Distance Error:</i> {distance_error}"
        )

        self.terminal.appendHtml(
            f"<i>Q Values:</i> {q_values} <hr />"
        )

    def check_user_define_usecase(self, filename_model, filename_img, filename_landmark):
        """
        Check which usecase that the user wants
        """

        filename_model = filename_model.split("/")
        filename_img = filename_img.split("/")
        filename_landmark = filename_landmark.split("/")

        # Ensure that user input file properly
        if "cardiac" in filename_model[-2] \
            and "cardiac" in filename_img[-1]\
            and "cardiac" in filename_landmark[-1] :
            return "CardiacMRI"
        elif "brain" in filename_model[-2] \
            and "brain" in filename_img[-1] \
            and "brain" in filename_landmark[-1]:
            return "BrainMRI"
        elif "ultrasound" in filename_model[-2] \
            and "fetal" in filename_img[-1] \
            and "fetal" in filename_landmark[-1]:
            return "FetalUS"
        else:
            return ""
    
    def set_paths(self, default_use_case):
        """
        Used to set paths before running the code
        """
        self.default_use_case = default_use_case
        if self.default_use_case == 'BrainMRI':
            # Default MRI
            self.fname_images.name = "./data/filenames/brain_test_files_new_paths.txt"
            self.fname_model.name = "./data/models/DQN_multiscale_brain_mri_point_pc_ROI_45_45_45/model-600000.data-00000-of-00001"
            self.fname_landmarks.name = "./data/filenames/brain_test_landmarks_new_paths.txt"
        elif self.default_use_case == 'CardiacMRI':
            # Default cardiac
            self.fname_images.name = "./data/filenames/cardiac_test_files_new_paths.txt"
            self.fname_model.name = './data/models/DQN_cardiac_mri/model-600000.data-00000-of-00001'
            self.fname_landmarks.name = "./data/filenames/cardiac_test_landmarks_new_paths.txt"
        elif self.default_use_case == 'FetalUS':
            # Default fetal
            self.fname_images.name = "./data/filenames/fetalUS_test_files_new_paths.txt"
            self.fname_model.name = './data/models/DQN_ultrasound/model-25000.data-00000-of-00001'
            self.fname_landmarks.name = "./data/filenames/fetalUS_test_landmarks_new_paths.txt"
        else:
            # User defined file selection
            self.fname_images.name = self.window.left_widget.fname_images
            self.fname_model.name = self.window.left_widget.fname_model
            self.fname_landmarks.name = self.window.left_widget.fname_landmarks

            # To tell the program which loader it should use
            self.default_use_case = self.check_user_define_usecase(self.fname_model.name, self.fname_images.name, self.fname_landmarks.name)

        self.window.usecase = self.default_use_case # indicate which use case currently

    def error_message_box(self):
        msg = QMessageBox()
        msg.setWindowTitle("Error on user defined settings")
        msg.setText("Please use appropriate model, image, and landmarks.")
        msg.setIcon(QMessageBox.Critical)

        # Clean up
        self.fname_landmarks.user_define = False
        self.fname_images.user_define = False
        self.fname_model.user_define = False
        self.window.left_widget.model_file_edit_text.setText("Default data selected")
        self.window.left_widget.landmark_file_edit_text.setText("Default data selected")
        self.window.left_widget.img_file_edit_text.setText("Default data selected")
        
        self.run_button.setStyleSheet("background-color:#4CAF50; color:white")
        self.run_button.setText("Start")
        # Display pop up message
        msg.exec_()

    def run_DQN(self):
        # if self.GPU_value:
            # os.environ['CUDA_VISIBLE_DEVICES'] = self.GPU_value

        # check input files
        if self.task_value == 'Play':
            self.selected_list = [self.fname_images]
        else:
            self.selected_list = [self.fname_images, self.fname_landmarks]

        self.METHOD = "DQN"
        # load files into env to set num_actions, num_validation_files
        try:
            init_player = MedicalPlayer(files_list=self.selected_list,
                                        data_type=self.default_use_case,
                                        screen_dims=IMAGE_SIZE,
                                        task='play')

            self.NUM_ACTIONS = init_player.action_space.n
            self.num_files = init_player.files.num_files
            # Create a thread to run background task
            self.worker_thread = WorkerThread(target_function=self.thread_function)
            self.worker_thread.window = self.window
            self.worker_thread.start()

        # If there is a problem with the loader, then user incorrectly add file
        except:
            self.terminal.appendHtml(f"<b><p style='color:red'> &#36; Error loading user defined settings. Please use appropriate model, image, and landmarks. </p></b>")
            self.error_message_box()
        

    def thread_function(self):
        """Run on secondary thread"""

        pred = OfflinePredictor(PredictConfig(
            model=Model(IMAGE_SIZE, FRAME_HISTORY, self.METHOD, self.NUM_ACTIONS, GAMMA),
            session_init=get_model_loader(self.fname_model.name),
            input_names=['state'],
            output_names=['Qvalue']))

        # demo pretrained model one episode at a time
        if self.task_value == 'Play':
            play_n_episodes(get_player(files_list=self.selected_list, viz=0.01,
                                        data_type=self.default_use_case,
                                        saveGif=self.GIF_value,
                                        saveVideo=self.video_value,
                                        task='play'),
                                pred, self.num_files, viewer=self.window)
        # run episodes in parallel and evaluate pretrained model
        elif self.task_value == 'Evaluation':
            play_n_episodes(get_player(files_list=self.selected_list, viz=0.01,
                                            data_type=self.default_use_case,
                                             saveGif=self.GIF_value,
                                             saveVideo=self.video_value,
                                             task='eval'),
                                pred, self.num_files, viewer=self.window)

    @property
    def window(self):
        return self._window

    @window.setter
    def window(self, window):
        self._window = window


###############################################################################
## Right Widget (Browse Mode)

class RightWidgetSettingsBrowseMode(QFrame):

    def __init__(self, *args, **kwargs):
        super(RightWidgetSettingsBrowseMode, self).__init__(*args, **kwargs)
        # Window and thread object
        self.window = None
        self.thread = WorkerThread(None)
        self.thread.pause = False

        # Widgets
        self.upButton = QToolButton(self)
        self.upButton.setArrowType(Qt.UpArrow)

        self.downButton = QToolButton(self)
        self.downButton.setArrowType(Qt.DownArrow)

        self.leftButton = QToolButton(self)
        self.leftButton.setArrowType(Qt.LeftArrow)

        self.rightButton = QToolButton(self)
        self.rightButton.setArrowType(Qt.RightArrow)

        self.inButton = QToolButton(self)
        self.inButton.setText('+')

        font = self.inButton.font()
        font.setBold(True)
        self.inButton.setFont(font)

        self.outButton = QToolButton(self)
        self.outButton.setText('-')
        font = self.outButton.font()
        font.setBold(True)
        self.outButton.setFont(font)

        self.zoomInButton = QToolButton(self)
        self.zoomInButton.setText('I')
        font = self.zoomInButton.font()
        font.setBold(True)
        self.zoomInButton.setFont(font)

        self.zoomOutButton = QToolButton(self)
        self.zoomOutButton.setText('O')
        font = self.zoomOutButton.font()
        font.setBold(True)
        self.zoomOutButton.setFont(font)

        # Placeholder for GUI filenames
        self.fname_images = filenames_GUI()
        self.fname_landmarks = filenames_GUI()

        ## Layout
        gridArrows = QGridLayout()
        gridArrows.setSpacing(5)
        gridArrows.addWidget(self.upButton, 0, 1)
        gridArrows.addWidget(self.downButton, 2, 1)
        gridArrows.addWidget(self.leftButton, 1, 0)
        gridArrows.addWidget(self.rightButton, 1, 2)
        gridArrows.addWidget(self.inButton, 0, 3)
        gridArrows.addWidget(self.outButton, 2, 3)
        gridArrows.addWidget(self.zoomInButton, 0, 4)
        gridArrows.addWidget(self.zoomOutButton, 2, 4)

        # Initialise grid/set spacing
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addLayout(gridArrows, 7, 0)

        gridNest = QGridLayout()
        gridNest.addLayout(grid, 1, 0, 10, 0)

        self.setLayout(gridNest)

        # Connections
        self.upButton.clicked.connect(self.on_clicking_up)
        self.downButton.clicked.connect(self.on_clicking_down)
        self.leftButton.clicked.connect(self.on_clicking_left)
        self.rightButton.clicked.connect(self.on_clicking_right)
        self.inButton.clicked.connect(self.on_clicking_in)
        self.outButton.clicked.connect(self.on_clicking_out)
        self.zoomInButton.clicked.connect(self.on_clicking_zoomIn)
        self.zoomOutButton.clicked.connect(self.on_clicking_zoomOut)

        self.show()

        # Flags for testing and env
        self.setStyleSheet("background:white")

        self.testing = False
        self.env = None

    @pyqtSlot()
    def on_clicking_up(self):
        if not self.testing and self.env:
            action = 1
            self.move_img(action)

    @pyqtSlot()
    def on_clicking_down(self):
        if not self.testing and self.env:
            action = 4
            self.move_img(action)

    @pyqtSlot()
    def on_clicking_left(self):
        if not self.testing and self.env:
            action = 3
            self.move_img(action)

    @pyqtSlot()
    def on_clicking_right(self):
        if not self.testing and self.env:
            action = 2
            self.move_img(action)

    @pyqtSlot()
    def on_clicking_in(self):
        if not self.testing and self.env:
            action = 0
            self.move_img(action)

    @pyqtSlot()
    def on_clicking_out(self):
        if not self.testing and self.env:
            action = 5
            self.move_img(action)

    @pyqtSlot()
    def on_clicking_zoomIn(self):
        if not self.testing and self.env and self.env.xscale > 1:
            self.env.adjustMultiScale(higherRes=True)
            self.move_img(-1)

    @pyqtSlot()
    def on_clicking_zoomOut(self):
        if not self.testing and self.env and self.env.xscale < 3:
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
        if self.default_use_case == 'BrainMRI':
            # Default MRI
            self.fname_images.name = "./data/filenames/brain_test_files_new_paths.txt"
            self.fname_landmarks.name = "./data/filenames/brain_test_landmarks_new_paths.txt"
        elif self.default_use_case == 'CardiacMRI':
            # Default cardiac
            self.fname_images.name = "./data/filenames/cardiac_test_files_new_paths.txt"
            self.fname_landmarks.name = "./data/filenames/cardiac_test_landmarks_new_paths.txt"
        elif self.default_use_case == 'FetalUS':
            # Default fetal
            self.fname_images.name = "./data/filenames/fetalUS_test_files_new_paths.txt"
            self.fname_landmarks.name = "./data/filenames/fetalUS_test_landmarks_new_paths.txt"
        else:
            # User defined file selection
            self.fname_images.name = self.window.left_widget.fname_images
            self.fname_landmarks.name = self.window.left_widget.fname_landmarks

            # To tell the program which loader it should use
            self.default_use_case = self.check_user_define_usecase(self.fname_images.name, self.fname_landmarks.name)

            if not self.default_use_case:
                self.error_message_box()
                self.default_use_case = self.which_usecase()
                return

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
        msg = QMessageBox()
        msg.setWindowTitle("Error on user defined settings")
        msg.setText("Please use appropriate model, image, and landmarks.")
        msg.setIcon(QMessageBox.Critical)

        # Clean up
        self.fname_landmarks.user_define = False
        self.fname_images.user_define = False
        self.window.left_widget.model_file_edit_text.setText("Default data selected")
        self.window.left_widget.landmark_file_edit_text.setText("Default data selected")
        self.window.left_widget.img_file_edit_text.setText("Default data selected")
        
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
            return "UserDefined"


################################################################################
## Main Function
# Responsible for execution of the whole application

if __name__ == "__main__":

    ########################################################################
    # PyQt GUI Code Section
    # Define application and viewer to run on the main thread
    # app = QApplication(sys.argv)
    # viewer_param = get_viewer_data()
    # right_settings = RightWidgetSettings()
    # window = Window(viewer_param, right_settings)
    #
    # # window.left_widget.thread = thread
    controller = Controller()
    sys.exit(controller.app.exec_())

    ########################################################################

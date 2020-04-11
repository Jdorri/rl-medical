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
## Right Widget

class filenames_GUI:
    def __init__(self):
        self.name = ""

class RightWidgetSettings(QFrame):
    terminal_signal = pyqtSignal(dict)
    SWITCH_WINDOW = pyqtSignal()
    MODE = 'DEFAULT MODE'

    def __init__(self, *args, **kwargs):
        super(RightWidgetSettings, self).__init__(*args, **kwargs)
        # Width and height settings
        self.setMaximumWidth(400)
        self.setMinimumHeight(800)

        # Thread and window object which will be used to gain access to primary
        # windows.
        self.thread = WorkerThread(None)
        self.window = None

        # Automatic, browse mode
        self.testMode = QPushButton('Automatic Mode', self)
        self.testMode.setCheckable(True)
        self.testMode.setChecked(True)
        self.browseMode = QPushButton('Browse Mode', self)
        self.browseMode.setCheckable(True)

        # Task
        self.task = QLabel('Task', self)
        self.play_button = QRadioButton("Play")
        self.play_button.setChecked(True)
        self.eval_button = QRadioButton("Evaluation")

        # Agent speed
        label_speed = QLabel("Agent Speed")
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

        # Temporary default file path
        self.fname_images = filenames_GUI()
        self.fname_landmarks = filenames_GUI()
        self.dtype = filenames_GUI()
        self.fname_logs_dir = "./data"

        ## Layout
        # Auto-browse mode layout
        gridMode = QGridLayout()
        gridMode.setContentsMargins(0, 0, 0, 20)
        gridMode.addWidget(self.testMode, 0, 0)
        gridMode.setHorizontalSpacing(0)
        gridMode.addWidget(self.browseMode, 0, 1)
        gridMode.setVerticalSpacing(2)

        # Task layout
        hbox_task = QHBoxLayout()
        hbox_task.setSpacing(30)
        hbox_task.addWidget(self.play_button)
        hbox_task.addWidget(self.eval_button)

        # Run layout
        hbox_run = QHBoxLayout()
        hbox_run.setSpacing(10)
        hbox_run.addWidget(self.run_button)
        hbox_run.addWidget(self.terminate_button)

        # Task, agent speed, run, layout
        grid = QGridLayout()
        grid.setVerticalSpacing(20) # spacing
        grid.addWidget(self.task, 1, 0)
        grid.addLayout(hbox_task, 2, 0)
        grid.addWidget(label_speed, 4, 0, 1, 2)
        grid.addWidget(self.speed_slider, 5, 0, 1, 2)
        grid.addItem(QSpacerItem(0, 30), 6, 0) # add space
        grid.addLayout(hbox_run, 7, 0)

        # Main layout
        vbox = QVBoxLayout()
        vbox.addLayout(gridMode)
        vbox.addLayout(grid)
        vbox.addItem(QSpacerItem(300, 50)) # spacer
        vbox.addWidget(label_log)
        vbox.addWidget(self.terminal)
        vbox.addStretch()

        self.setLayout(vbox)

        # Event handler
        self.browseMode.clicked.connect(self.on_clicking_browseMode)
        self.run_button.clicked.connect(self.on_clicking_run)
        self.terminal_signal.connect(self.terminal_signal_handler)
        self.terminate_button.clicked.connect(self.on_clicking_terminate)
        
        # CSS styling for some widget components
        self.run_button.setStyleSheet("background-color:#4CAF50; color:white")
        self.terminate_button.setStyleSheet("background-color:#f44336; color:white")

        self.show()

        # Flags for testing
        self.testing = False
        self.test_click = None
    
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
        self.run_button.setText("Start")
        self.run_button.setStyleSheet("background-color:#4CAF50; color:white")
        
        # Reset simple image viewer
        self.window.widget.reset()
    
    def which_task(self):
        """
        Determine which radio button task is checked
        """
        if self.play_button.isChecked():
            return "Play"
        else:
            return "Evaluation"

    @pyqtSlot()
    def on_clicking_run(self):
        """
        Event handler (slot) for when the button is clicked
        """
        if self.run_button.text() == "Start":
            self.thread.terminate = False
            self.task_value = self.which_task()
            self.terminal.appendPlainText(f"> Begin {self.task_value} Mode")
            self.GIF_value = False
            self.video_value = False
            self.run_button.setText("Pause")
            self.window.statusbar.showMessage("Running")
            self.run_button.setStyleSheet("background-color:orange; color:white")
            self.run_DQN()
        elif self.run_button.text() == "Resume":
            self.thread.pause = False
            self.run_button.setText("Pause")
            self.run_button.setStyleSheet("background-color:orange; color:white")
            self.window.statusbar.showMessage("Running")
        else:
            self.thread.pause = True
            self.run_button.setText("Resume")
            self.run_button.setStyleSheet("background-color:#4CAF50; color:white")
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

    @pyqtSlot()
    def on_clicking_browseMode(self):
        self.thread.terminate = True
        self.SWITCH_WINDOW.emit()

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
        init_player = MedicalPlayer(files_list=self.selected_list,
                                    # data_type=self.dtype,
                                    data_type=self.dtype.name,
                                    screen_dims=IMAGE_SIZE,
                                    task='play')
        self.NUM_ACTIONS = init_player.action_space.n
        self.num_files = init_player.files.num_files
        # Create a thread to run background task
        self.worker_thread = WorkerThread(target_function=self.thread_function)
        self.worker_thread.start()

        print(init_player._location)

    def thread_function(self):
        """Run on secondary thread"""

        pred = OfflinePredictor(PredictConfig(
            model=Model(IMAGE_SIZE, FRAME_HISTORY, self.METHOD, self.NUM_ACTIONS, GAMMA),
            session_init=get_model_loader(self.fname_model),
            input_names=['state'],
            output_names=['Qvalue']))

        # demo pretrained model one episode at a time
        if self.task_value == 'Play':
            play_n_episodes(get_player(files_list=self.selected_list, viz=0.01,
                                        data_type=self.dtype.name,
                                        saveGif=self.GIF_value,
                                        saveVideo=self.video_value,
                                        task='play'),
                                pred, self.num_files, viewer=self.window)
        # run episodes in parallel and evaluate pretrained model
        elif self.task_value == 'Evaluation':
            play_n_episodes(get_player(files_list=self.selected_list, viz=0.01,
                                            data_type=self.dtype.name,
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


class RightWidgetSettingsBrowseMode(QFrame):

    SWITCH_WINDOW = pyqtSignal()
    KEY_PRESSED = pyqtSignal(QEvent)
    MODE = 'BROWSE MODE'

    def __init__(self, *args, **kwargs):
        super(RightWidgetSettingsBrowseMode, self).__init__(*args, **kwargs)

        # window title
        self.setWindowTitle('Anatomical Landmark Detection')
        self.window = None
        self.thread = WorkerThread(None)
        self.thread.pause = False

        # initialise labels
        # self.img_file = QLabel('Image file', self)
        # self.mode = QLabel('Mode', self)

        # initialise widgets
        self.testMode = QPushButton('Test Mode', self)
        self.browseMode = QPushButton('Browse Mode', self)
        self.browseMode.setCheckable(True)
        self.browseMode.setChecked(True)

        self.img_file_edit = QPushButton('Upload Images', self)
        self.exit = QPushButton('Exit', self)

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

        # temporary default file paths
        self.fname_images = filenames_GUI()
        self.fname_landmarks = filenames_GUI()
        self.dtype = filenames_GUI()

        ### LAYOUT ###
        gridMode = QGridLayout()
        gridMode.setSpacing(1)
        gridMode.addWidget(self.testMode, 0, 0)
        gridMode.addWidget(self.browseMode, 0, 1)

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

        # initialise grid/set spacing
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self.img_file_edit, 3, 0)
        grid.addLayout(gridArrows, 7, 0)
        grid.addWidget(self.exit, 12, 0)

        gridNest = QGridLayout()
        gridNest.addLayout(gridMode, 0, 0)
        gridNest.addLayout(grid, 1, 0, 10, 0)

        self.setLayout(gridNest)
        # self.setGeometry(100, 100, 350, 400)

        # connections
        self.testMode.clicked.connect(self.on_clicking_testMode)
        self.img_file_edit.clicked.connect(self.on_clicking_browse_images)
        self.exit.clicked.connect(self.on_clicking_exit)
        self.upButton.clicked.connect(self.on_clicking_up)
        self.downButton.clicked.connect(self.on_clicking_down)
        self.leftButton.clicked.connect(self.on_clicking_left)
        self.rightButton.clicked.connect(self.on_clicking_right)
        self.inButton.clicked.connect(self.on_clicking_in)
        self.outButton.clicked.connect(self.on_clicking_out)
        self.zoomInButton.clicked.connect(self.on_clicking_zoomIn)
        self.zoomOutButton.clicked.connect(self.on_clicking_zoomOut)

        self.show()

        # Flags for testing
        self.testing = False
        self.test_click = None

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

    @pyqtSlot()
    def on_clicking_testMode(self):
        self.SWITCH_WINDOW.emit()

    @pyqtSlot()
    def on_clicking_exit(self):
        if not self.testing:
            self.close_it

    @pyqtSlot()
    def on_clicking_browse_images(self):
        if not self.testing:
            self.fname_images.name, _ = QFileDialog.getOpenFileName(None, None,
                "./data/filenames", filter="txt files (*test_files*.txt)")
            self.fname_images.name, _ = QFileDialog.getOpenFileName(None, None,
                "./data/filenames", filter="txt files (*landmarks*.txt)")
            self.load_img()

    @pyqtSlot()
    def close_it(self):
        self.close()

    def load_img(self):
        self.task_value = None
        self.selected_list = [self.fname_images, self.fname_landmarks]

        self.env = get_player(files_list=self.selected_list, viz=0.01,
                        saveGif=False, saveVideo=False, task='browse',
                        data_type=self.dtype.name)
        self.env.stepManual(act=-1, viewer=self.window)
        self.env.display()

    def move_img(self, action):
        self.env.stepManual(action, self.window)
        QApplication.processEvents()
        self.window.update()


class Controller:
    def __init__(self, display=True, default_use_case='BrainMRI'):
        self.default_use_case = default_use_case
        self.window1, self.window2 = None, None
        self.app = QApplication(sys.argv)
        self.viewer_param = get_viewer_data()
        self.show_defaultMode()
        self.window1.show()
        # self.show_browseMode()
        # self.window2.show()

    def show_defaultMode(self):
        # Init the window
        self.right_settings = RightWidgetSettings()
        self.window1 = Window(self.viewer_param, self.right_settings)
        self.right_settings.window = self.window1
        self.set_paths()

        # Close previous window
        if self.window2:
            self.window2.hide()

        # Open new window with new right_settings
        self.window1.right_widget.SWITCH_WINDOW.connect(self.show_browseMode)

    def show_browseMode(self):
        # Init the window
        self.right_settings = RightWidgetSettingsBrowseMode()
        self.window2 = Window(self.viewer_param, self.right_settings)
        self.right_settings.window = self.window2
        self.load_defaults()

        # Close previous window
        if self.window1:
            self.window1.hide()

        # Open new window with new right_settings
        self.window2.right_widget.SWITCH_WINDOW.connect(self.show_defaultMode)

    def load_defaults(self):
        self.set_paths()
        self.right_settings.load_img()

    def set_paths(self):
        assert self.default_use_case in ['BrainMRI', 'CardiacMRI', 'FetalUS'], "Invalid default use case"
        self.right_settings.dtype.name = self.default_use_case
        if self.default_use_case == 'BrainMRI':
            # Default MRI
            self.right_settings.fname_images.name = "./data/filenames/brain_test_files_new_paths.txt"
            self.right_settings.fname_model = "./data/models/DQN_multiscale_brain_mri_point_pc_ROI_45_45_45/model-600000.data-00000-of-00001"
            self.right_settings.fname_landmarks.name = "./data/filenames/brain_test_landmarks_new_paths.txt"
        elif self.default_use_case == 'CardiacMRI':
            # Default cardiac
            self.right_settings.fname_images.name = "./data/filenames/cardiac_test_files_new_paths.txt"
            self.right_settings.fname_model = './data/models/DQN_cardiac_mri/model-600000.data-00000-of-00001'
            self.right_settings.fname_landmarks.name = "./data/filenames/cardiac_test_landmarks_new_paths.txt"
        elif self.default_use_case == 'FetalUS':
            # Default fetal
            self.right_settings.fname_images.name = "./data/filenames/fetalUS_test_files_new_paths.txt"
            self.right_settings.fname_model = './data/models/DQN_ultrasound/model-25000.data-00000-of-00001'
            self.right_settings.fname_landmarks.name = "./data/filenames/fetalUS_test_landmarks_new_paths.txt"

    @staticmethod
    def allWidgets_setCheckable(parentQWidget):
        ''' Method to eet every widget to checkable for so the .isChecked()
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

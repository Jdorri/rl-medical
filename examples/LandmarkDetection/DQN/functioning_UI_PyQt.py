import sys
from PyQt5.QtWidgets import*
from PyQt5.QtCore import Qt, pyqtSlot
# from DQN import Model, get_player

from DQN import get_player, Model, get_config

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
MEMORY_SIZE = 1e5#6
# consume at least 1e6 * 27 * 27 * 27 bytes
INIT_MEMORY_SIZE = MEMORY_SIZE // 20 #5e4
# each epoch is 100k played frames
STEPS_PER_EPOCH = 10000 // UPDATE_FREQ * 10
# num training epochs in between model evaluations
EPOCHS_PER_EVAL = 2
# the number of episodes to run during evaluation
EVAL_EPISODE = 50

###############################################################################

# custom class
class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # window title
        self.setWindowTitle('Anatomical Landmark Detection')

        # initialise labels
        self.GPU = QLabel('GPU', self)
        self.load = QLabel('Load Model', self)
        self.task = QLabel('Task', self)
        self.algorithm = QLabel('Algorithm', self)
        self.img_file = QLabel('File 1: Images', self)
        self.landmark_file = QLabel('File 2: Landmarks', self)
        self.GIF = QLabel('Save GIF', self)
        self.video = QLabel('Save Video', self)
        self.log_dir = QLabel('Store Logs', self)
        self.name = QLabel('Experiment Name', self)

        # initialise widgets
        self.GPU_edit = QLineEdit()
        self.load_edit = QPushButton('Browse', self)
        self.task_edit = QComboBox()
        self.algorithm_edit = QComboBox()
        self.img_file_edit = QPushButton('Browse', self)
        self.landmark_file_edit = QPushButton('Browse', self)
        self.GIF_edit =  QCheckBox()
        self.video_edit = QCheckBox()
        self.log_dir_edit = QPushButton('Browse', self)
        self.name_edit = QLineEdit()
        self.run = QPushButton('Run', self)
        self.exit = QPushButton('Exit', self)

        # add widget functionality
        self.task_edit.addItems(['Play', 'Evaluation', 'Train'])
        self.algorithm_edit.addItems(['DQN', 'Double', 'Dueling', 'Dueling Double'])

        # temporary default file paths
        self.fname_images = "/homes/jd3114/Documents/Group Project/rl-medical/examples/LandmarkDetection/DQN/data/filenames/image_files.txt"
        # self.fname_images = "/Users/phaedonmit/Documents/Python/rl-medical/examples/LandmarkDetection/DQN/data/filenames/image_files.txt"
        # self.fname_images = './data/filenames/image_files.txt'
        self.fname_model = "/homes/jd3114/Documents/Group Project/rl-medical/examples/LandmarkDetection/DQN/data/models/DQN_multiscale_brain_mri_point_pc_ROI_45_45_45/model-600000.data-00000-of-00001"
        # self.fname_model = "/Users/phaedonmit/Documents/Python/rl-medical/examples/LandmarkDetection/DQN/data/models/DQN_multiscale_brain_mri_point_pc_ROI_45_45_45/model-600000.data-00000-of-00001"

        self.fname_logs_dir = "/homes/jd3114/Documents/Group Project/rl-medical/examples/LandmarkDetection/DQN/data"

        # initialise grid/set spacing
        grid = QGridLayout()
        grid.setSpacing(10)

        # add widgets to grid
        grid.addWidget(self.task, 1, 0)
        grid.addWidget(self.task_edit, 1, 1)

        grid.addWidget(self.algorithm, 2, 0)
        grid.addWidget(self.algorithm_edit, 2, 1)

        grid.addWidget(self.load, 3, 0)
        grid.addWidget(self.load_edit, 3, 1)

        grid.addWidget(self.GPU, 4, 0)
        grid.addWidget(self.GPU_edit, 4, 1)

        grid.addWidget(self.img_file, 5, 0)
        grid.addWidget(self.img_file_edit, 5, 1)

        grid.addWidget(self.landmark_file, 6, 0)
        grid.addWidget(self.landmark_file_edit, 6, 1)

        grid.addWidget(self.GIF, 7, 0)
        grid.addWidget(self.GIF_edit, 7, 1)

        grid.addWidget(self.video, 8, 0)
        grid.addWidget(self.video_edit, 8, 1)

        grid.addWidget(self.log_dir, 9, 0)
        grid.addWidget(self.log_dir_edit, 9, 1)

        grid.addWidget(self.name, 10, 0)
        grid.addWidget(self.name_edit, 10, 1)

        grid.addWidget(self.run, 11, 0)
        grid.addWidget(self.exit, 12, 0)

        self.setLayout(grid)
        self.setGeometry(100, 100, 350, 400)

        # connections
        self.load_edit.clicked.connect(self.on_clicking_browse_model)
        self.img_file_edit.clicked.connect(self.on_clicking_browse_images)
        self.landmark_file_edit.clicked.connect(self.on_clicking_browse_landmarks)
        self.log_dir_edit.clicked.connect(self.on_clicking_browse_logs_dir)
        self.run.clicked.connect(self.on_clicking_run)
        self.exit.clicked.connect(self.close_it)

        self.show()

    @pyqtSlot()
    def on_clicking_run(self):
        self.GPU_value = self.GPU_edit.text()
        self.DQN_variant_value = self.algorithm_edit.currentText()
        self.task_value = self.task_edit.currentText()
        self.GIF_value = self.GIF_edit.isChecked()
        self.video_value = self.video_edit.isChecked()
        self.name_value = self.name_edit.text()
        #self.run_DQN()
        print(self.task_value)
        self.close()

    @pyqtSlot()
    def on_clicking_browse_model(self):
        self.fname_model, _ = QFileDialog.getOpenFileName()
        print(self.fname_model)

    @pyqtSlot()
    def on_clicking_browse_images(self):
        self.fname_images, _ = QFileDialog.getOpenFileName()
        print(self.fname_images)

    @pyqtSlot()
    def on_clicking_browse_landmarks(self):
        self.fname_landmarks, _ = QFileDialog.getOpenFileName()

    @pyqtSlot()
    def on_clicking_browse_logs_dir(self):
        self.fname_logs_dir, _ = QFileDialog.getOpenFileName()

    def run_DQN(self):
          if self.GPU_value:
              os.environ['CUDA_VISIBLE_DEVICES'] = self.GPU_value

          # check input files
          if self.task_value == 'Play':
              selected_list = [self.fname_images]
          else:
              selected_list = [self.fname_images, self.fname_landmarks]


          METHOD = self.DQN_variant_value
          # load files into env to set num_actions, num_validation_files
          init_player = MedicalPlayer(files_list=selected_list,
                                      screen_dims=IMAGE_SIZE,
                                      task='play')
          NUM_ACTIONS = init_player.action_space.n
          num_files = init_player.files.num_files

          if self.task_value != 'Train':
              pred = OfflinePredictor(PredictConfig(
                  model=Model(IMAGE_SIZE, FRAME_HISTORY, METHOD, NUM_ACTIONS, GAMMA ),
                  session_init=get_model_loader(self.fname_model),
                  input_names=['state'],
                  output_names=['Qvalue']))
              # demo pretrained model one episode at a time
              if self.task_value == 'Play':
                  play_n_episodes(get_player(files_list=selected_list, viz=0.01,
                                             saveGif=self.GIF_value,
                                             saveVideo=self.video_value,
                                             task='play'),
                                  pred, num_files)
              # run episodes in parallel and evaluate pretrained model
          elif self.task_value == 'Evaluation':
                  play_n_episodes(get_player(files_list=selected_list, viz=0.01,
                                             saveGif=self.GIF_value,
                                             saveVideo=self.video_value,
                                             task='eval'),
                                  pred, num_files)
          else:  # train model
              logger_dir = os.path.join(self.fname_logs_dir, self.name_value)
              logger.set_logger_dir(logger_dir)
              config = get_config(selected_list)
              if self.load_value:  # resume training from a saved checkpoint
                  config.session_init = get_model_loader(self.load_value)
              launch_train_with_config(config, SimpleTrainer())

    @pyqtSlot()
    def close_it(self):
        self.close()

# QApplication instance
app = QApplication(sys.argv)

# custom class instance
window = MainWindow()

app.exec_()

window.run_DQN()

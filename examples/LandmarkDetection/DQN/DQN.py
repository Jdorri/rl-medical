def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn
warnings.simplefilter("ignore", category=PendingDeprecationWarning)
warnings.simplefilter("ignore", category=FutureWarning)

import numpy as np
import os
import sys
import time
import argparse
from collections import deque
import tensorflow as tf
from RL.medical import MedicalPlayer, FrameStack
from tensorpack.input_source import QueueInput
from tensorpack_medical.models.conv3d import Conv3D
from tensorpack_medical.models.pool3d import MaxPooling3D
from RL.common import Evaluator, eval_model_multithread, play_n_episodes
from RL.DQNModel import Model3D as DQNModel
from RL.expreplay import ExpReplay

from tensorpack import (PredictConfig, OfflinePredictor, get_model_loader,
                        logger, TrainConfig, ModelSaver, PeriodicTrigger,
                        ScheduledHyperParamSetter, ObjAttrParam,
                        HumanHyperParamSetter, argscope, RunOp, LinearWrap,
                        FullyConnected, PReLU, SimpleTrainer,
                        launch_train_with_config)

from GUI.thread import WorkerThread
# from viewer import SimpleImageViewer, Window # This wont work on GPU cluster so uncomment for now
import pickle

from PyQt5.QtWidgets import QApplication
from RL.freeze_variables import freeze_variables

###############################################################################
# BATCH SIZE USED IN NATURE PAPER IS 32 - MEDICAL IS 256
BATCH_SIZE = 48
# BREAKOUT (84,84) - MEDICAL 2D (60,60) - MEDICAL 3D (26,26,26)
IMAGE_SIZE = (45, 45, 45)
# how many frames to keep
# in other words, how many observations the network can see
FRAME_HISTORY = 4
# number of steps to take with the episilon greedy policy before comitting it
# memory.
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
# or
STEPS_PER_EVAL = 10000
# the number of episodes to run during evaluation
EVAL_EPISODE = 50
# Max number of training epochs
MAX_EPOCHS = 1000
# Number of pretraining steps (only relevant for HITL)
NUM_PRETRAIN = 100000

###############################################################################

def get_player(directory=None, files_list= None, data_type=None, viz=False,
               task='play', saveGif=False, saveVideo=False):
    # in atari paper, max_num_frames = 30000
    env = MedicalPlayer(directory=directory, screen_dims=IMAGE_SIZE,
                        viz=viz, saveGif=saveGif, saveVideo=saveVideo,
                        task=task, files_list=files_list, data_type=data_type, max_num_frames=1500)

    if task not in ['browse','train']:
        # in training, env will be decorated by ExpReplay, and history
        # is taken care of in expreplay buffer
        # otherwise, FrameStack modifies self.step to save observations into a queue
        env = FrameStack(env, FRAME_HISTORY)
    return env

###############################################################################

class Model(DQNModel):
    def __init__(self,IMAGE_SIZE, FRAME_HISTORY, METHOD, NUM_ACTIONS, GAMMA, trainable_variables):
        super(Model, self).__init__(IMAGE_SIZE, FRAME_HISTORY, METHOD, NUM_ACTIONS, GAMMA)
        self.conv_freeze = "CNN" not in trainable_variables
        if "FC" not in trainable_variables:
            self.fc_freeze = "FC_intermediate" not in trainable_variables
            self.final_layer_freeze = "FC_final" not in trainable_variables
        else:
            self.fc_freeze = False
            self.final_layer_freeze = False


    def _get_DQN_prediction(self, image):
        """ image: [0,255]

        :returns predicted Q values"""
        # normalize image values to [0, 1]
        image = image / 255.0

        with argscope(Conv3D, nl=PReLU.symbolic_function, use_bias=True):
            # core layers of the network
            with freeze_variables(stop_gradient=False, skip_collection=self.conv_freeze):#conv
                conv = (LinearWrap(image)
                    .Conv3D('conv0', out_channel=32,
                            kernel_shape=[5,5,5], stride=[1,1,1])
                    .MaxPooling3D('pool0',2)
                    .Conv3D('conv1', out_channel=32,
                            kernel_shape=[5,5,5], stride=[1,1,1])
                    .MaxPooling3D('pool1',2)
                    .Conv3D('conv2', out_channel=64,
                            kernel_shape=[4,4,4], stride=[1,1,1])
                    .MaxPooling3D('pool2',2)
                    .Conv3D('conv3', out_channel=64,
                            kernel_shape=[3,3,3], stride=[1,1,1])
                    # .MaxPooling3D('pool3',2)
                    )

        if 'Dueling' not in self.method:
            with freeze_variables(stop_gradient=False, skip_collection=self.fc_freeze):#fc
                lq = (conv
                    .FullyConnected('fc0', 512).tf.nn.leaky_relu(alpha=0.01)
                    .FullyConnected('fc1', 256).tf.nn.leaky_relu(alpha=0.01)
                    .FullyConnected('fc2', 128).tf.nn.leaky_relu(alpha=0.01)())
            with freeze_variables(stop_gradient=False, skip_collection=self.final_layer_freeze):#fclast
                Q = FullyConnected('fct', lq, self.num_actions, nl=tf.identity)
        else:
            # Dueling DQN or Double Dueling
            # state value function
            with freeze_variables(stop_gradient=False, skip_collection=self.fc_freeze):#fc
                lv = (conv
                    .FullyConnected('fc0V', 512).tf.nn.leaky_relu(alpha=0.01)
                    .FullyConnected('fc1V', 256).tf.nn.leaky_relu(alpha=0.01)
                    .FullyConnected('fc2V', 128).tf.nn.leaky_relu(alpha=0.01)())
            with freeze_variables(stop_gradient=False, skip_collection=self.final_layer_freeze):#fclast
                V = FullyConnected('fctV', lv, 1, nl=tf.identity)
                # advantage value function
                la = (conv
                    .FullyConnected('fc0A', 512).tf.nn.leaky_relu(alpha=0.01)
                    .FullyConnected('fc1A', 256).tf.nn.leaky_relu(alpha=0.01)
                    .FullyConnected('fc2A', 128).tf.nn.leaky_relu(alpha=0.01)())
            with freeze_variables(stop_gradient=False, skip_collection=self.final_layer_freeze):#fclast
                As = FullyConnected('fctA', la, self.num_actions, nl=tf.identity)

            Q = tf.add(As, V - tf.reduce_mean(As, 1, keepdims=True))

        return tf.identity(Q, name='Qvalue')

###############################################################################

def get_config(files_list, data_type, trainable_variables):
    """This is only used during training."""
    expreplay = ExpReplay(
        predictor_io_names=(['state'], ['Qvalue']),
        player=get_player(task='train', files_list=files_list, data_type=data_type),
        state_shape=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        memory_size=MEMORY_SIZE,
        init_memory_size=INIT_MEMORY_SIZE,
        init_exploration=0.8, #0.0
        ###############################################################################
        # HITL UPDATE
        update_frequency=INIT_UPDATE_FREQ,
        ###############################################################################
        history_len=FRAME_HISTORY,
        arg_type=data_type
    )

    return TrainConfig(
        # dataflow=expreplay,
        data=QueueInput(expreplay),
        model=Model(IMAGE_SIZE, FRAME_HISTORY, METHOD, NUM_ACTIONS, GAMMA, trainable_variables),
        callbacks=[
            ModelSaver(),
            PeriodicTrigger(
                RunOp(DQNModel.update_target_param, verbose=True),
                # update target network every 10k steps
                every_k_steps=10000 // UPDATE_FREQ),
            expreplay,
            ScheduledHyperParamSetter('learning_rate',
                                      [(60, 4e-4), (100, 2e-4)]),
            ScheduledHyperParamSetter(
                ObjAttrParam(expreplay, 'exploration'),
                # 1->0.1 in the first million steps
                [(0, 0.8), (1000000, 0.1), (32000000, 0.01)],
                interp='linear',
                step_based=True),
###############################################################################
# HITL UPDATE
# Here the number of steps taken in the environment is increased from 0, during
# the pretraining phase, to 4 to allow the agent to take 4 steps in the env
# between each TD update.
            ScheduledHyperParamSetter(
                ObjAttrParam(expreplay, 'update_frequency'),

                [(0, INIT_UPDATE_FREQ), (NUM_PRETRAIN, UPDATE_FREQ)],

                interp=None, step_based=True),

###############################################################################

            PeriodicTrigger(
                Evaluator(nr_eval=EVAL_EPISODE, input_names=['state'],
                          output_names=['Qvalue'], files_list=files_list,
                          data_type=data_type,
                          get_player_fn=get_player),
                every_k_steps=STEPS_PER_EVAL),
            HumanHyperParamSetter('learning_rate'),
        ],
        steps_per_epoch=STEPS_PER_EPOCH,
        max_epoch=MAX_EPOCHS,
    )

def get_viewer_data():
    """Used to get viewer initialisation data"""
    ########################################################################
    # PyQt GUI Code Section
    with open("data/default_data/default_data.pickle", "rb") as f:
        viewer_param = pickle.load(f)

    return viewer_param

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

###############################################################################
###############################################################################

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--gpu', help='comma separated list of GPU(s) to use.')
    parser.add_argument('--load', help='load model to resume traning')
    parser.add_argument('--transferModel',  nargs='+', help='load model for transfer learning' , type=str)
    parser.add_argument('--trainable',  nargs='+', help='list of trainable variables' , type=str, default=['CNN', 'FC'])
    parser.add_argument('--task', help='task to perform. Must load a pretrained model if task is "play" or "eval"',
                        choices=['play', 'eval', 'train'], default='train')
    parser.add_argument('--algo', help='algorithm',
                        choices=['DQN', 'Double', 'Dueling','DuelingDouble'],
                        default='DQN')
    parser.add_argument('--type', help='the dataset to use',
                        choices=['BrainMRI', 'CardiacMRI', 'FetalUS'],
                        default=False)
    parser.add_argument('--files', type=argparse.FileType('r'), nargs='+',
                        help="""Filepath to the text file that comtains list of images.
                                Each line of this file is a full path to an image scan.
                                For (task == train or eval) there should be two input files ['images', 'landmarks']""")
    parser.add_argument('--saveGif', help='save gif image of the game',
                        action='store_true', default=False)
    parser.add_argument('--saveVideo', help='save video of the game',
                        action='store_true', default=False)
    parser.add_argument('--logDir', help='store logs in this directory during training',
                        default='train_log')
    parser.add_argument('--name', help='name of current experiment for logs',
                        default='experiment_1')
    parser.add_argument('--HITL', help='perform HITL experiment', default=False, type=str2bool)

    parser.add_argument('--directory', help='file name to store evaluation results',
                        default=None)
    args = parser.parse_args()

    # f1 = filenames_GUI()
    # f2 = filenames_GUI()
    # f1.name = './data/filenames/brain_test_files_new_paths.txt'
    # f2.name = './data/filenames/brain_test_landmarks_new_paths.txt'
    # files_list = [f1, f2]

    if args.gpu:
        os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu

    # check input files
    if args.task == 'play':
        error_message = """Wrong input files {} for {} task - should be 1 \'images.txt\' """.format(len(args.files), args.task)
        assert len(args.files) == 1
    else:
        error_message = """Wrong input files {} for {} task - should be 2 [\'images.txt\', \'landmarks.txt\'] """.format(len(args.files), args.task)
        assert len(args.files) == 2, (error_message)

    METHOD = args.algo
    # load files into env to set num_actions, num_validation_files
    init_player = MedicalPlayer(files_list=args.files, #files_list=files_list,
                                data_type=args.type,
                                screen_dims=IMAGE_SIZE,
                                task='play')
    NUM_ACTIONS = init_player.action_space.n
    num_files = init_player.files.num_files

    if args.task != 'train':
        assert args.load is not None
        pred = OfflinePredictor(PredictConfig(
            model=Model(IMAGE_SIZE, FRAME_HISTORY, METHOD, NUM_ACTIONS, GAMMA, args.trainable ),
            session_init=get_model_loader(args.load),
            input_names=['state'],
            output_names=['Qvalue']))
        # demo pretrained model one episode at a time
        if args.task == 'play':
            play_n_episodes(get_player( files_list=args.files,
                                        data_type=args.type,
                                        viz=0,
                                        saveGif=args.saveGif,
                                        saveVideo=args.saveVideo,
                                        task='play'),
                            pred, num_files, viewer=None)

        # run episodes in parallel and evaluate pretrained model
        elif args.task == 'eval':
            play_n_episodes(get_player(directory=args.directory,
                                        files_list=args.files,
                                        data_type=args.type,
                                        viz=0,
                                        saveGif=args.saveGif,
                                        saveVideo=args.saveVideo,
                                        task='eval'),
                                        pred, num_files, viewer=None)

     ########################################################################

    else:  # train model
        print(f"TRAINABLE PARAMETERS: {args.trainable}")
        logger_dir = os.path.join(args.logDir, args.name)
        logger.set_logger_dir(logger_dir)
        if args.HITL:
            INIT_UPDATE_FREQ = 0
        else:
            INIT_UPDATE_FREQ = 4
        config = get_config(args.files, args.type, args.trainable)
        if args.load:  # resume training from a saved checkpoint
            session_init = get_model_loader(args.load)
        elif args.transferModel:
            ignore_list = ["Adam",
                           "alpha",
                           "huber_loss",
                           "beta1_power",
                           "beta2_power",
                           "predict_reward",
                           "learning_rate",
                           "local_step",
                           "QueueInput",
                           "global_step",
                           "SummaryGradient",
                        ]#always ignore these

            if not bool(args.transferModel[1:]):#transfer all layers of none specified
                pass
            else:
                if 'CNN' not in args.transferModel[1:]:#ignore CNN part
                    ignore_list.append("conv")
                if 'FC' not in args.transferModel[1:]:#ignore FC
                    if 'FC_intermediate' not in args.transferModel[1:]:
                        ignore_list.append("fc0")
                        ignore_list.append("fc1")
                        ignore_list.append("fc2")
                    if 'FC_final' not in args.transferModel[1:]:
                        ignore_list.append("fct")

            session_init = get_model_loader(args.transferModel[0])
            reader, variables = session_init._read_checkpoint_vars(args.transferModel[0])

            ignore = [var for var in variables if any([i in var for i in ignore_list])]
            session_init.ignore = [i if i.endswith(':0') else i + ':0' for i in ignore]
            config.session_init = session_init


        launch_train_with_config(config, SimpleTrainer())

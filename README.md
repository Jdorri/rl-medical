# **A**natomical **L**andmark **D**etection and **D**emonstration **I**nterface (ALADDIN) <img src="examples/LandmarkDetection/DQN/images/aladdin.png" width="100" />

ALADDIN is a platform offering automated solutions for the detection of anatomical landmarks using reinforcement learning (RL) agents, complete with a unified visualisation suite. The tool is targeted at both medical imaging professionals and machine learning researchers.

The work was completed as part of the course [Software Engineering Practice & Group Project](https://www.imperial.ac.uk/computing/current-students/courses/70048/) (MSc AI, Imperial College) and builds on the [deep RL framework](https://github.com/amiralansary/rl-medical) of the [Biomedical Image Anaysis Group](https://biomedia.doc.ic.ac.uk). 

## Results

Here are a few examples of learned landmark detection agents on unseen data. These are displayed on a custom graphical user interface, the core product:

* Detecting the anterior commissure (AC) point in adult brain MRI.
<p align="center">
<img src="examples/LandmarkDetection/DQN/videos/brain.gif" width="500">
</p>

* Detecting the apex point in short-axis cardiac MRI.
<p align="center">
<img src="examples/LandmarkDetection/DQN/videos/cardiac.gif" width="500">
</p>

* Detecting the cavum septum pellucidum (CSP) point in fetal head ultrasound.
<p align="center">
<img src="examples/LandmarkDetection/DQN/videos/fetal.gif" width="500">
</p>

## Installation

### Dependencies

+ Python=3.8
+ [cycler=0.10.0](https://pypi.org/project/Cycler/)
+ [tensorflow=1.14.0](https://pypi.org/project/tensorflow/)
+ [tensorpack=0.9.5](https://github.com/tensorpack/tensorpack)
+ [opencv-python=4.2.0.32](https://pypi.org/project/opencv-python/)
+ [pillow](https://pypi.org/project/Pillow/)
+ [gym](https://pypi.org/project/gym/)
+ [SimpleITK](https://pypi.org/project/SimpleITK/)
+ [PyQt5](https://pypi.org/project/PyQt5/)
+ [ipython](https://pypi.org/project/ipython/)
+ [matplotlib](https://pypi.org/project/matplotlib/)
+ [pandas](https://pypi.org/project/pandas/)
+ [seaborn](https://pypi.org/project/seaborn/)

### Procedure

Follow the following steps (in order) to install the required dependencies.

1. Clone this repository
2. ``` cd rl-medical ```
3. ``` pip install -r requirements.txt ```
4. ``` pip install -U git+https://github.com/amiralansary/rl-medical.git ```

## Running the Code

The ALADDIN platform has two distinct modes of use: 'GUI' and 'DQN'. Follow the relevant steps (in order) after installing all required packages.

- To view the main product with pre-trained models, follow **GUI**.   
- To train your own model/view detailed logs, follow **DQN**.

**Note**: the main product is the GUI; DQN serves as a backend for training and logging models. Before running a DQN training script, also keep in mind that a model is usually trained for at least 2 days and requires use of GPU.

*Please email a member of the group or our supervisor if you have any issues with code execution.*

### GUI

The GUI facilitates running, visualising, and evaluating the performance of pre-trained RL agents in locating landmarks on medical image datasets (brain, cardiac, fetal).

1. Open ```Terminal```
2. Go to the [main directory](examples/LandmarkDetection/DQN) by using the command ```cd examples/LandmarkDetection/DQN```
3. Run the GUI by using the command ```python controller.py```
4. For further instructions on how to use the GUI, open the 'Application Help' window on the GUI through the 'Help' menu.

### DQN

The DQN software allows experts to train and evaluate RL models with different hyperparameter choices using a basic DQN implementation as well as [HITL](https://en.wikipedia.org/wiki/Human-in-the-loop) and [Transfer Learning](https://en.wikipedia.org/wiki/Transfer_learning) extensions.

1. Open ```Terminal```
2. Go to the [main directory](examples/LandmarkDetection/DQN) by using the command ```cd examples/LandmarkDetection/DQN```
3. Run the relevant command depending on usage and extensions chosen (see subsections below). For more information about options and flags, see usage documentation below.

##### Train - Basic

```
python DQN.py --task train --algo DQN --gpu 0 --files './data/filenames/local/brain_train_files_new_paths.txt' './data/filenames/local/brain_train_landmarks_new_paths.txt' --type 'BrainMRI' --HITL False
```

##### Train - Transfer Learning 

```
python DQN.py --task train --algo DQN --gpu 0 --files './data/filenames/local/brain_train_files_new_paths.txt' './data/filenames/local/brain_train_landmarks_new_paths.txt' --type 'BrainMRI' --HITL False --transferModel data/models/DQN_multiscale_brain_mri_point_pc_ROI_45_45_45/model-600000 CNN FC
```

##### Evaluate

```
python DQN.py --task eval --algo DQN --gpu 0 --load data/models/DQN_multiscale_brain_mri_point_pc_ROI_45_45_45/model-600000 --files './data/filenames/image_files.txt' './data/filenames/landmark_files.txt' --type 'BrainMRI'
```

##### Test

```
python DQN.py --task play --algo DQN --gpu 0 --load data/models/DQN_multiscale_brain_mri_point_pc_ROI_45_45_45/model-600000 --files './data/filenames/image_files.txt' --type 'BrainMRI'
```

##### Usage

```
usage: DQN.py [-h] [--gpu GPU] [--load LOAD] [--task {play,eval,train}]
              [--algo {DQN,Double,Dueling,DuelingDouble}]
              [--files FILES [FILES ...]] [--saveGif] [--saveVideo]
              [--logDir LOGDIR] [--name NAME][--type {'BrainMRI', 'CardiacMRI', 'FetalUS'}]
              [--HITL {True, False}] [--transferModel MODEL_PATH [VARIABLE_GROUPS ...]]

optional arguments:
  -h, --help            show this help message and exit
  --gpu GPU             comma separated list of GPU(s) to use.
  --load LOAD           load model
  --task {play,eval,train}
                        task to perform. Must load a pretrained model if task
                        is "play" or "eval"
  --algo {DQN,Double,Dueling,DuelingDouble}
                        algorithm
  --files FILES [FILES ...]
                        Filepath to the text file that comtains list of
                        images. Each line of this file is a full path to an
                        image scan. For (task == train or eval) there should
                        be two input files ['images', 'landmarks']
  --saveGif             save gif image of the game
  --saveVideo           save video of the game
  --logDir LOGDIR       store logs in this directory during training
  --name NAME           name of current experiment for logs
  --type                type of dataset can be either 'BrainMRI', 'CardiacMRI', or 'FetalUS'
  --HITL                flag to indicate (for training) to use HITL.
                        In order to run in HITL mode, the required training files need to
                        be included to load human experience on the human experience buffer.
  --transferModel       To use transfer learning you specify the argument --transferModel which
                        as argument takes the path to a model followed by and optional list
                        of variable groups to transfer after the path. Specifying no groups will
                        transfer everything.

                        The variable groups are (as specifed in the report)
                        1. CNN: all convolutional layers
                        2. FC: all fully connected layers
                        3. FC_intermediate: All fully connected layers excluding the final one
                        4. FC_final: Only the final fully connected layer

                        You can also specify which variables that should be trainable by the argument
                        --trainable as trainable groups in any combo of variable groups from above (i.e.)
                        --trainable CNN FC will train everything and is the default value
                        --trainable FC will only train variable group FC and so on
```

## Folder Structure

For a description of the folder structure of the main directory, please click [here](folder_structure.md).

## Authors

- **Harry Coppock**: hgc19@imperial.ac.uk
- **James Dorricott**: jd3114@imperial.ac.uk
- **Alexander Gaskell**: aeg19@imperial.ac.uk
- **Faidon Mitzalis**: fm1710@imperial.ac.uk
- **Olle Nilsson**: oen19@imperial.ac.uk
- **Maleakhi Wijaya**: maw219@imperial.ac.uk

## Supervisor

- **Amir Alansary**: a.alansary14@imperial.ac.uk

## Citation

If you use this code in your research, please cite these paper:

```
@article{alansary2019evaluating,
  title={{Evaluating Reinforcement Learning Agents for Anatomical Landmark Detection}},
  author={Alansary, Amir and Oktay, Ozan and Li, Yuanwei and Le Folgoc, Loic and
          Hou, Benjamin and Vaillant, Ghislain and Kamnitsas, Konstantinos and
          Vlontzos, Athanasios and Glocker, Ben and Kainz, Bernhard and Rueckert, Daniel},
  journal={Medical Image Analysis},
  year={2019},
  publisher={Elsevier}
}
 ```

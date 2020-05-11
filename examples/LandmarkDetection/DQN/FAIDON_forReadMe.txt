Train:
python DQN.py --task train --algo DQN --gpu 0 --files './data/filenames/local/brain_train_files_new_paths.txt' './data/filenames/local/brain_train_landmarks_new_paths.txt' --type 'BrainMRI' --HITL False

This command can be used to train a model on the specified dataset (includes paths to a list of images and a list of landmarks). The type of dataset 'BrainMRI', 'CardiacMRI' or 'FetalUS' needs to be specified.
In order to run in HITL mode, the required training files need to be included to load human experience on the human experience buffer.

Evaluate:
python DQN.py --task eval --algo DQN --gpu 0 --load data/models/DQN_multiscale_brain_mri_point_pc_ROI_45_45_45/model-600000 --files './data/filenames/image_files.txt' './data/filenames/landmark_files.txt' --type 'BrainMRI'
This command can be used to evaluate the model on the specified dataset from the command line (includes paths to a list of images and a list of landmarks). The type of dataset 'BrainMRI', 'CardiacMRI' or 'FetalUS' needs to be specified.

Play: 
python DQN.py --task play --algo DQN --gpu 0 --load data/models/DQN_multiscale_brain_mri_point_pc_ROI_45_45_45/model-600000 --files './data/filenames/image_files.txt' --type 'BrainMRI'
This command can be used to evaluate the model on the specified dataset from the command line (includes paths to a list of images and a list of landmarks). The type of dataset 'BrainMRI', 'CardiacMRI' or 'FetalUS' needs to be specified.

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

 

TL:

The variable groups are (as specifed in the report)

CNN: all convolutuional layers
FC: all fully connected layers
FC_intermediate: All fully connected layers excluding the final one 
FC_final: Only the final fully connected layer

to use transfer learning you specify the argument --transferModel which as argument takes the path to a model followed by and optional list of variable groups to transfer
after the path. Specifying no groups will tranfer everything.

The below command will transfer from model data/models/DQN_multiscale_brain_mri_point_pc_ROI_45_45_45/model-60000 and transfers groups CNN and FC. The list of variable groups can be any combo of the
groups listed above.

python DQN.py --task train --algo DQN --gpu 0 --files './data/filenames/local/brain_train_files_new_paths.txt' './data/filenames/local/brain_train_landmarks_new_paths.txt' --type 'BrainMRI' --HITL False --transferModel data/models/DQN_multiscale_brain_mri_point_pc_ROI_45_45_45/model-600000 CNN FC

You can also specify which variables that should be trainable by the argument --trainable
as trainable groups in any combo of variable groups from above, for example

--trainable CNN FC will train everything and is the default value
--trainable FC will only train variable group FC and so on
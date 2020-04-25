################################################################################
## Script to evaluate multiple models on test dataset and store results
# Author: Faidon
################################################################################

import subprocess
import os
import csv


data_type = "FetalUS"
imperial_cluster = True
csvfile = 'Reward_and_Q_log.csv'

################################################################################################
# Step 1 - Set paths for model and test dataset
if imperial_cluster:
    redir = '/vol/biomedic/users/aa16914/shared/data/RL_data/' 
    # model = "/volumes/project/2019/545/g1954503/oen19/LandmarkDetection/001/output/001/model-600000"
    directory = "/vol/project/2019/545/g1954503/fm1710/LandmarkDetection/FetalUS/001/output/FetalUS001/" 
else:
    redir = 'data/filenames/'
    # model = "/volumes/project/2019/545/g1954503/oen19/LandmarkDetection/001/output/001/model-600000"
    directory = "/volumes/project/2019/545/g1954503/oen19/LandmarkDetection/FetalUS/001/output/FetalUS001/"

################################################################################################
# Step 2 - Set test dataset paths depending on where it's running and datatype
if data_type == 'BrainMRI':
    # Default MRI
    fname_images = f"{redir}brain_test_files_new_paths.txt"
    fname_landmarks = f"{redir}brain_test_landmarks_new_paths.txt"
elif data_type == 'CardiacMRI':
    # Default cardiac
    fname_images = f"{redir}cardiac_test_files_new_paths.txt"
    fname_landmarks = f"{redir}cardiac_test_landmarks_new_paths.txt"
elif data_type == 'FetalUS':
    # Default fetal
    fname_images = f"{redir}fetalUS_test_files_new_paths.txt"
    fname_landmarks = f"{redir}fetalUS_test_landmarks_new_paths.txt"

################################################################################################
# Step 3 - Flag start of model assessment
with open(csvfile, 'a') as outcsv:
                fields= ['START MODEL', directory]
                writer = csv.writer(outcsv)
                writer.writerow(map(lambda x: x, fields))
################################################################################################
# Step 4 - Run test datasets on all model checkpoints
for filename in os.listdir(directory):
    if (filename.endswith(".index")):
        model_name = os.path.splitext(filename)[0]
        model = os.path.join(directory, model_name)
        with open(csvfile, 'a') as outcsv:
                fields= ['START CHECKPOINT', model]
                writer = csv.writer(outcsv)
                writer.writerow(map(lambda x: x, fields))        
 
        if imperial_cluster:
            subprocess.run(["python3", "DQN.py", "--task", "eval", "--algo", "DQN", "--gpu", "0", "--load",
                            model, "--files", 
                            fname_images, fname_landmarks,  "--type", data_type ])
        else:
            subprocess.run(["python", "DQN.py", "--task", "eval", "--algo", "DQN", "--gpu", "0", "--load",
                            model, "--files", 
                            fname_images, fname_landmarks,  "--type", data_type ])                                        
################################################################################################
# Step 5 - Flag end of model assessment
with open(csvfile, 'a') as outcsv:
    fields= ['FINISH DIRECTORY']
    writer = csv.writer(outcsv)
    writer.writerow(map(lambda x: x, fields))
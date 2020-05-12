import os
import subprocess
import glob



user = '...' # put your username here
type_ = 'LandmarkDetection'
task = 'train'
algo = 'DQN'
data_type ='FetalUS'



# model = "'/vol/project/2019/545/g1954503/oen19/LandmarkDetection/003/output/003/model-600000'"
# transferModel = "'/vol/project/2019/545/g1954503/oen19/LandmarkDetection/003/output/003/model-600000'"#CardiacMRI basecase
# transferModel = "'/vol/project/2019/545/g1954503/oen19/LandmarkDetection/001/output/001/model-600000'"#BrainMRI basecase
# to_Transfer = "CNN DQN"

discription = """HITL experimentation with 50 50 sampling ratio HC"""

home = os.environ['HOME']
local_branch_path = os.path.join(home, 'Documents/rl-medical/')#path to where the code is
# local_branch_path = os.path.join(home, '/vol/project/2019/545/g1954503/oen19/rl-medical/')#path to where the code is

data_path = os.path.join(home, '/vol/biomedic/users/aa16914/shared/data/RL_data')#path to where the raw data is
output_path = os.path.join(home, '/vol/project/2019/545/g1954503/')#path to where to store the results
venv_path = os.path.join(home, '/vol/bitbucket/oen19/rl-medical/')#path to where the virural environment is





#make directories
def mkdir_p(dir, level):
    '''make a directory (dir) if it doesn't exist'''
    if not os.path.exists(dir):
        os.mkdir(dir)



def get_next_case_number(directories):
    if not directories:
        return '001'
    max_case_nr = -float('inf')
    for directory in directories:
        case_nr = int(directory)
        max_case_nr = max(max_case_nr, case_nr)

    next_case_nr = '0'*(3-len(str(max_case_nr + 1))) + str(max_case_nr + 1)
    return next_case_nr


user_path = output_path + f"{user}/"
mkdir_p(user_path, 'user')#create user
type_path = user_path + f"{type_}/"
mkdir_p(type_path, 'type')#create subfolder
type_path = type_path + f"{data_type}/"
mkdir_p(type_path, 'type')#create subfolder
sub_directories = next(os.walk(type_path))[1]
case_number = get_next_case_number(sub_directories)
case_path = type_path + f"{case_number}/"
mkdir_p(case_path, 'case')#create case folder
input_path = case_path + "input/"
mkdir_p(input_path, 'input')#create case input folder
output_path = case_path + "output/"
mkdir_p(output_path, 'output')#create case output folder

description_file = os.path.join(input_path, f"{data_type}{case_number}.txt")
with open(description_file, 'w') as ds:
    ds.write(discription)

#Make submission file

job_file = os.path.join(input_path, f"{data_type}{case_number}.sh")
if data_type == "BrainMRI":
    files = "'/vol/biomedic/users/aa16914/shared/data/RL_data/brain_train_files_new_paths.txt' '/vol/biomedic/users/aa16914/shared/data/RL_data/brain_train_landmarks_new_paths.txt'"
elif data_type == "CardiacMRI":
    files = "'/vol/biomedic/users/aa16914/shared/data/RL_data/cardiac_train_files_new_paths.txt' '/vol/biomedic/users/aa16914/shared/data/RL_data/cardiac_train_landmarks_new_paths.txt'"
elif data_type == "FetalUS":
    files = "'/vol/biomedic/users/aa16914/shared/data/RL_data/fetalUS_train_files_new_paths.txt' '/vol/biomedic/users/aa16914/shared/data/RL_data/fetalUS_train_landmarks_new_paths.txt'"


with open(job_file, 'w') as fh:


    fh.writelines("#!/bin/bash\n")
    fh.writelines(f"#SBATCH --job-name=harrys_baby.job\n")
    fh.writelines(f"#SBATCH --output={output_path}{data_type}{case_number}.out\n")
    fh.writelines(f"#SBATCH --error={output_path}{data_type}{case_number}.err\n")
    fh.writelines("#SBATCH --mail-type=ALL\n")
    fh.writelines(f"#SBATCH --mail-user={user}\n")
    fh.writelines("source /vol/cuda/10.0.130-cudnn7.6.4.38/setup.sh\n")
    fh.writelines("TERM=vt100\n") # or TERM=xterm
    fh.writelines("/usr/bin/nvidia-smi\n")
    fh.writelines("uptime\n")
    fh.writelines(f"python {local_branch_path}examples/{type_}/DQN/DQN.py "
                                                            f"--task {task} "
                                                            f"--algo {algo} "
                                                            f"--gpu 0 "
                                                            # f"--load {model} "
                                                            # f"--transferModel {transferModel} {to_Transfer} "
                                                            f"--type {data_type} "
                                                            f"--files {files} "
                                                            f"--logDir {output_path} "
                                                            f"--name {data_type}{case_number}")


subprocess.call(f"(. {venv_path}bin/activate && sbatch -w kingfisher {job_file})", shell=True)

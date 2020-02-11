import os
import subprocess

user = 'oen19'
type_ = 'LandmarkDetection' 
job = 'testing'
task = 'train'
algo = 'DQN'


home = os.environ['HOME']
local_branch_path = os.path.join(home, 'Documents/rl-medical/')#path to where the code is
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
sub_directories = next(os.walk(type_path))[1]
case_number = get_next_case_number(sub_directories)
case_path = type_path + f"{case_number}/"
mkdir_p(case_path, 'case')#create case folder
input_path = case_path + "input/"
mkdir_p(input_path, 'input')#create case input folder
output_path = case_path + "output/"
mkdir_p(output_path, 'output')#create case output folder

#Make submission file

job_file = os.path.join(input_path, f"{case_number}.sh")
files = "'/vol/biomedic/users/aa16914/shared/data/RL_data/brain_train_files_new_paths.txt' '/vol/biomedic/users/aa16914/shared/data/RL_data/brain_train_landmarks_new_paths.txt'"
# files = "'/vol/biomedic/users/aa16914/shared/data/RL_data/cardiac_train_files_new_paths.txt' '/vol/biomedic/users/aa16914/shared/data/RL_data/cardiac_train_landmarks_new_paths.txt'"
# files = "'/vol/biomedic/users/aa16914/shared/data/RL_data/fetalUS_train_files_new_paths.txt' '/vol/biomedic/users/aa16914/shared/data/RL_data/fetalUS_train_landmarks_new_paths.txt'"
model = "'/vol/project/2019/545/g1954503/oen19/LandmarkDetection/003/output/003/model-600000'"
with open(job_file, 'w') as fh:


    fh.writelines("#!/bin/bash\n")
    fh.writelines(f"#SBATCH --job-name={case_number}.job\n")
    fh.writelines(f"#SBATCH --output={output_path}{case_number}.out\n")
    fh.writelines(f"#SBATCH --error={output_path}{case_number}.err\n")
    # fh.writelines("#SBATCH --time=2-00:00\n")
    # fh.writelines("#SBATCH --mem=12000\n")
    # fh.writelines("#SBATCH --qos=normal\n")
    # fh.writelines("#SBATCH --gres=gpu:1\n")
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
                                                            f"--load {model} "
                                                            f"--files {files} " 
                                                            f"--logDir {output_path} "
                                                            f"--name {case_number}")


#SSH into cluster and submit
sshProcess = subprocess.Popen(['ssh',
                               "gpucluster.doc.ic.ac.uk"],
                               stdin=subprocess.PIPE,
                               stdout = subprocess.PIPE,
                               universal_newlines=True,
                               bufsize=0)
sshProcess.stdin.write(f"source {venv_path}bin/activate\n")
sshProcess.stdin.write(f"sbatch {job_file}\n")
sshProcess.stdin.close()
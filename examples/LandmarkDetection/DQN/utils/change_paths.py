import os

new_base_path = "/vol/biomedic/users/aa16914/shared/data/RL_data/cardiac_mri_adult"
file_path = "/vol/biomedic/users/aa16914/shared/data/RL_data/"

data_files = ["cardiac_test_files.txt", "cardiac_train_files.txt"]
landmark_files = ["cardiac_test_landmarks.txt", "cardiac_train_landmarks.txt"]

file_full_path = os.path.join(file_path, landmark_files[0])

print(file_path)

with open(file_full_path) as fp:
    for line in fp.readlines():
        new_path = '/'.join(new_base_path.split('/') + line.split('/')[7:])
        # print(new_path)
        write_path = os.path.join(file_path, "cardiac_test_landmarks_new_paths.txt")
        f_new=open(write_path, "a+")
        f_new.write(new_path)
    f_new.close()
            


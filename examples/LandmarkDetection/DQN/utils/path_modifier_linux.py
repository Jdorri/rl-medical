
img_path = f"./data/filenames/fetalUS_train_files_new_paths.txt"
lmk_path = f"./data/filenames/fetalUS_train_landmarks_new_paths.txt"
new_path = "/run/user/1000/gvfs/smb-share:domain=IC,server=fs-vol-project.doc.ic.ac.uk,share=project,user=oen19/"


with open("./data/filenames/fetalUS_train_files_new_paths_linux.txt",'w') as new_file:
    with open(img_path) as old_file:
        for line in old_file:
            new_file.write(line.replace("/volumes/project/", new_path))

with open("./data/filenames/fetalUS_train_landmarks_new_paths_linux.txt",'w') as new_file:
    with open(lmk_path) as old_file:
        for line in old_file:
            new_file.write(line.replace("/volumes/project/", new_path))
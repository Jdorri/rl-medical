import os
import glob

list_of_files = glob.glob('*.pickle')
for f in list_of_files:
    new_name = f[:3] + '_BrainMRI' + f[3:]
    os.rename(f, new_name)

list_of_files = glob.glob('*.pickle')
print(list_of_files)

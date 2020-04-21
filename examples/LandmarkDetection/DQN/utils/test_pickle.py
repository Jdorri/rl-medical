import pickle

path = './data/HITL/log_2020-04-06-16:31:14.pickle'
with open(path, 'rb') as f:
    x = pickle.load(f)

[print(a) for a in x]


# import glob
# import os
#
# list_of_files = glob.glob('./data/HITL/*.pickle')
# latest_file = max(list_of_files, key=os.path.getctime)
# print(latest_file)

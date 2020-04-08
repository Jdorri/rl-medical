import pickle
import glob
import os

# Load the created file
list_of_files = glob.glob('./data/HITL/*.pickle')
latest_file = max(list_of_files, key=os.path.getctime)
with open(latest_file, 'rb') as f:
    log = pickle.load(f)

episodes = 0
states = -1
for l in log:
    episodes += 1
    for state in l['states']:
        states += 1
        # print(state)
    print('\n')

print('Episodes: ', episodes)
print('States: ', states)

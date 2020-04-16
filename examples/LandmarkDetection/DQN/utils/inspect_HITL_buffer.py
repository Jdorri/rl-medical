import pickle
import glob
import os

def show_latest():
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

    print('For the most recent pickle file: ')
    print('Episodes: ', episodes)
    print('States: ', states)
    print('')

def show_all(data_type):
    list_of_files = glob.glob(f'./data/HITL/*{data_type}*.pickle')

    tot_episodes = tot_states = 0
    for file in list_of_files:
        with open(file, 'rb') as f:
            log = pickle.load(f)

        episodes = 0
        states = -1
        for l in log:
            episodes += 1
            for state in l['states']:
                states += 1

        tot_episodes += episodes
        tot_states += states

    print(f'Total for {data_type}: ')
    print('Episodes: ', tot_episodes)
    print('States: ', tot_states)
    print('')

print('')
show_latest()
for d in ['BrainMRI','CardiacMRI','FetalUS']:
    show_all(d)

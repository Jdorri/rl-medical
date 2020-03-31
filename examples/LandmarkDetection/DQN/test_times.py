import timeit
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

###############################################################################
# BATCH SIZE USED IN NATURE PAPER IS 32 - MEDICAL IS 256
BATCH_SIZE = 48
# BREAKOUT (84,84) - MEDICAL 2D (60,60) - MEDICAL 3D (26,26,26)
IMAGE_SIZE = (45, 45, 45)
# how many frames to keep
# in other words, how many observations the network can see
FRAME_HISTORY = 4
# the frequency of updating the target network
UPDATE_FREQ = 4
# DISCOUNT FACTOR - NATURE (0.99) - MEDICAL (0.9)
GAMMA = 0.9 #0.99
# REPLAY MEMORY SIZE - NATURE (1e6) - MEDICAL (1e5 view-patches)
MEMORY_SIZE = 1e5#6
# consume at least 1e6 * 27 * 27 * 27 bytes
INIT_MEMORY_SIZE = MEMORY_SIZE // 20 #5e4
# each epoch is 100k played frames
STEPS_PER_EPOCH = 10000 // UPDATE_FREQ * 10
# num training epochs in between model evaluations
EPOCHS_PER_EVAL = 2
# the number of episodes to run during evaluation
EVAL_EPISODE = 50

METHOD = "DQN"

###############################################################################

def play_episode():

    fname_images = filenames_GUI()
    fname_images.name = "./data/filenames/timing_test.txt"
    fname_model = "./data/models/DQN_multiscale_brain_mri_point_pc_ROI_45_45_45/model-600000.data-00000-of-00001"  
    selected_list = [fname_images]  
    # load files into env to set num_actions, num_validation_files
    init_player = MedicalPlayer(files_list=selected_list,
                                screen_dims=IMAGE_SIZE,
                                task='play')
    NUM_ACTIONS = init_player.action_space.n
    num_files = init_player.files.num_files

    pred = OfflinePredictor(PredictConfig(
        model=Model(IMAGE_SIZE, FRAME_HISTORY, METHOD, NUM_ACTIONS, GAMMA ),
        session_init=get_model_loader(fname_model),
        input_names=['state'],
        output_names=['Qvalue']))    
    play_n_episodes(get_player(files_list=selected_list, viz=False,
                                        saveGif=False,
                                        saveVideo=False,
                                        task='play'),
                            pred, 1, False)

if __name__ == '__main__':
    # Step 0 - Initialise variables
    recorded_times = []
    section_names = []
    number = 1
    
    # Step 1 - Import modules
    recorded_times.append(timeit.timeit("import functioning_UI_PyQt", number=1))
    section_names.append("Import Modules")
    print(f'{section_names[-1]} section lasted: {recorded_times[-1]:.3f}')
    from functioning_UI_PyQt import *

    # Step 2 - GUI user selection
    recorded_times.append(5+recorded_times[-1])
    section_names.append("User Selection")   

    # Step 3 - Launch GUI
    recorded_times.append(timeit.timeit("play_episode()", number=number, setup="from __main__ import play_episode")/number+recorded_times[-1])
    section_names.append("Run Episode")
    print(f'{section_names[-1]} section lasted: {recorded_times[-1]:.3f}')

    #for plotting purposes
    recorded_times.append("Single Landmark Test")
    section_names.append("name")   

    # Step 4 - Plot Results
    sns.set(style="whitegrid")

    df = pd.DataFrame([recorded_times], columns=section_names)

    # Initialize the matplotlib figure
    f, ax = plt.subplots(figsize=(6, 1.5))

    # Load the example car crash dataset


    sns.set_color_codes("pastel")


    sns.barplot(x=section_names[2], y="name", data=df,
                label=section_names[2], color="b")
    sns.barplot(x=section_names[1], y="name", data=df,
                label=section_names[1], color="g")
    sns.barplot(x=section_names[0], y="name", data=df,
                label=section_names[0], color="y")



    # Add a legend and informative axis label
    ax.legend(ncol=2, loc="lower right", frameon=True)
    ax.set(xlim=(0, 30), ylabel="",
        xlabel="Cumulative Time (s)")
    sns.despine(left=True, bottom=True)
    plt.legend(loc='upper right')
    plt.savefig('timings_plot.png', bbox_inches='tight')
################################################################################
## Script to plot evaluation results from multiple models
# Author: Faidon
################################################################################

import subprocess
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()

############################################################################################################
# Step 0 - Choose paths to plot
filename = "./results/eval_logs/logs_eval_CardiacMRI.csv"
model_name = ""
model_path = ""
checkpoint = ""
entry = 0

df_complete = pd.DataFrame(columns=['model_path', 'model_name',  'image_path', 'checkpoint', 'score', 'distance_error'])
df_summary = pd.DataFrame(columns=['model_path', 'model_name',  'checkpoint', 'mean_score', 'mean_distance_error', 'std_distance_error'])
mounted = os.path.exists("/volumes/project/")

############################################################################################################
# Step 1 - Read logs and populate pandas
with open(filename, newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in spamreader:
        if row:
            if row[0]=="FINISH":
                continue
            elif row[0]=="START":
                details = row[1].split(',')
                if details[0]=="MODEL":
                    folder = os.path.basename(os.path.dirname(details[1]))
                    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(details[1]))), 'input', folder+'.txt')
                    if mounted:
                        if folder=="001":
                            model_name="BrainMRI Baseline DQN"
                        elif folder=="002":
                            model_name="Test local point"
                        elif folder=="003":
                            model_name="Cardiac Baseline DQN"                            
                        elif folder=="004":
                            model_name="Default model in DQN folder"    
                        elif folder =="006":
                            model_name = "BrainMRI Baseline DQN - RERUN"
                        else:
                            with open(model_path.replace("/vol/","/volumes/"), 'r') as file:
                                model_name = file.read().replace('\n', '')
                    else:
                        model_name = folder
                else:
                    checkpoint = int((os.path.basename(details[1])).split('-')[1])
            else:
                details = row[0].split(',')
                df_complete.loc[entry] = [model_path, model_name, details[0], checkpoint, float(details[1]), float(details[2]) ]
                entry += 1

############################################################################################################
# Step 2 - Generate summary dataframe
entry = 0
for model in df_complete.model_name.unique():
    df =  df_complete[df_complete['model_name']==model]
    for checkpoint in df.checkpoint.unique():
        df_check = df[df['checkpoint']==checkpoint]
        df_summary.loc[entry] = [df_check['model_path'].iloc[0], df_check['model_name'].iloc[0], checkpoint, df_check.mean()['score'], df_check.mean()['distance_error'],
                                df_check.std()['distance_error']]
        entry += 1

print(df_summary[['model_name', 'checkpoint', 'mean_distance_error', 'std_distance_error']])        

############################################################################################################
# Step 2 - Plot results
ax = sns.lineplot(x="checkpoint", y="distance_error",
                hue="model_name", style="model_name", ci="sd",
                 markers=True, dashes=False, data=df_complete)
# ax = sns.lineplot(x="checkpoint", y="mean_distance_error",
#                 # hue="std_distance_error", style="std_distance_error",
#                  markers=True, dashes=False, data=df_summary)
# control x and y limits
plt.ylim(0, 12)
plt.xlim(0, None)
plt.savefig('results/plots/plot.png')
plt.show()
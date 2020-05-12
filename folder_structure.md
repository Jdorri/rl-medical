# Folder Structure

The following are description of files on main directory ```examples/LandmarkDetection/DQN```.

- **controller.py**: doorway for launching GUI application
- **DQN.py**: contains functions and parameters to initialise the RL environment and agent (main script for command line use)
- **GUI_tests.py**: unit tests for GUI application
- **data**: contains model, landmark, image data
- **GUI**: contains codes related to GUI (frontend)
  - **text**: contains text resource for GUI
  - **css**: contains css resource for GUI
  - **application_help.py**: application help window widget
  - **FilenamesGUI.py**: class for storing file path
  - **left_widget.py**: all widgets to the left side of the main window
  - **plot_3d.py**: 3d plot widget
  - **right_widget_automatic.py**: all widgets to the right side of the main window (automatic mode)
  - **right_widget_browse.py**: all widgets to the right side of the main window (browse mode)
  - **terminal.py**: terminal widget
  - **thread.py**: threading separating GUI thread from RL algorithm thread
  - **viewer.py**: controls and creates GUI simulation and various plots
  - **window.py**: integrate left,viewer, and right widgets
- **RL**: contains codes related to algorithm (backend)
  - **common.py**: contains functions to run evaluation using RL agent
  - **dataReader.py**: contains functions to load and pre-process images from Brain MRI, Cardiac MRI and Fetal US datasets
  - **DQNModel.py**: defines class for the Model of the RL agent for 3D images
  - **expreplay.py**: contains classes for defining and using the agent and human experience buffers
  - **freeze_variables.py**: contains functions to freeze selected parameters in tensorpack model
  - **medical.py**: defines class for the MedicalPlayer which defines the RL environment using the 3D images
- **images**: contains application image resources (i.e. icon, logo, etc)
- **videos**: contains application video resources (for README)
- **utils**: contains other utilities
- **results**: contains result logs, result plots and scripts for batch evaluation and plotting results
  - **evaluate_models.py**: script to evaluate multiple models on test dataset and store results
  - **plot_results.py**: script to plot evaluation results from multiple models stored in log files
  - **eval_logs**: folder contains log files (.csv) with the mean distance error and score on the test datasets
  - **plots**: contains figures of the key results of the experiments carried out in the project

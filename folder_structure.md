# Folder Structure

The following are description of files on main directory ```examples\LandmarkDetection\DQN```.

- **controller.py**: doorway for launching GUI application
- **DQN.py**: 
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
  - **common.py**:
  - **dataReader.py**:
  - **DQNModel.py**:
  - **expreplay.py**:
  - **freeze_variables.py**:
  - **medical.py**:
- **images**: contains application image resources (i.e. icon, logo, etc)
- **videos**: contains application video resources (for README)
- **utils**: contains other utilities
- **results**: contains result logs, result plots and scripts for batch evaluation and plotting results

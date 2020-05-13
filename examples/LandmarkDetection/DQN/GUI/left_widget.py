################################################################################
## Left widget file 
# Author: Maleakhi, Alex, Jamie, Faidon, Olle, Harry
################################################################################

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

    
################################################################################
## Left Widget
# Control several of main application functionalities (positioned on the left of image widget).

class LeftWidgetSettings(QFrame):
    """
    Left widget controlling GUI elements settings.
    """
    # Constant
    DEFAULT_DATA_NOTIFICATION = "<i> Default data selected </i>"

    def __init__(self, window):
        """
        Constructor for left widget.

        :param window: instance of Window object
        """

        super().__init__()
        # Window object to access windows components
        self.window = window # Store window object to enable control over windows functionality
        
        self.title = QLabel("<b> Data Manager </b>")

        ## Default file mode
        self.simple_title = QLabel("Default Data")
        self.brain_button = QRadioButton("Brain")
        self.cardiac_button = QRadioButton("Cardiac")
        self.ultrasound_button = QRadioButton("Fetal")
        self.brain_button.setChecked(True)

        # Disable cardiac and ultrasound since data is private
        # For demo purposes we won't disable
        self.cardiac_button.setEnabled(False)
        self.ultrasound_button.setEnabled(False)

        ## Advance file mode
        self.advance_title = QLabel("Custom Data")
        # Load model settings
        self.model_file = QLabel('Load Model', self)
        self.model_file_edit = QPushButton('Browse', self)
        self.model_file_edit_text = QLabel(LeftWidgetSettings.DEFAULT_DATA_NOTIFICATION)

        # Load landmark settings
        self.landmark_file = QLabel('Load Landmark', self)
        self.landmark_file_edit = QPushButton('Browse', self)
        self.landmark_file_edit_text = QLabel(LeftWidgetSettings.DEFAULT_DATA_NOTIFICATION)

        # Upload image settings
        self.img_file = QLabel('Load Image', self)
        self.img_file_edit = QPushButton('Browse', self)
        self.img_file_edit_text = QLabel(LeftWidgetSettings.DEFAULT_DATA_NOTIFICATION)

        # Logo settings
        self.logo = QLabel()
        pixmap_logo = QPixmap("./images/image.png")
        pixmap_logo = pixmap_logo.scaledToHeight(40)
        self.logo.setPixmap(pixmap_logo)

        # Load and clear button (for custom data)
        self.load_button = QPushButton("Load", self)
        self.clear_button = QPushButton("Clear", self)
        self.load_button.hide()

        # Quick help
        self.quick_help = QuickHelp()
        self.quick_help.hide() # by default hide
        
        ## Manage layout
        # Default data settings layout
        hbox_simple = QHBoxLayout()
        hbox_simple.setSpacing(20)
        hbox_simple.addWidget(self.brain_button)
        hbox_simple.addWidget(self.cardiac_button)
        hbox_simple.addWidget(self.ultrasound_button)

        # Browse + Layout
        hbox_model = QHBoxLayout()
        hbox_model.setSpacing(20)
        hbox_model.addWidget(self.model_file_edit)
        hbox_model.addWidget(self.model_file_edit_text)
        
        hbox_image = QHBoxLayout()
        hbox_image.setSpacing(20)
        hbox_image.addWidget(self.img_file_edit)
        hbox_image.addWidget(self.img_file_edit_text)

        hbox_landmark = QHBoxLayout()
        hbox_landmark.setSpacing(20)
        hbox_landmark.addWidget(self.landmark_file_edit)
        hbox_landmark.addWidget(self.landmark_file_edit_text)

        hbox_load = QHBoxLayout()
        # Note: space is used as placeholder for GUI consistency
        self.space = QLabel("")
        self.space.show()
        self.space.setStyleSheet("margin-top:30px; margin-bottom: 0px")
        hbox_load.addWidget(self.load_button)
        hbox_load.addWidget(self.clear_button)
        hbox_load.addWidget(self.space)
        
        # Main Layout
        vbox = QVBoxLayout()
        vbox.setSpacing(20)
        vbox.addWidget(self.title)
        vbox.addWidget(self.simple_title)
        vbox.addLayout(hbox_simple)
        vbox.addWidget(QLabel("<hr />"))
        vbox.addWidget(self.advance_title)
        vbox.addWidget(self.img_file)
        vbox.addLayout(hbox_image)
        vbox.addItem(QSpacerItem(300, 10))
        vbox.addWidget(self.landmark_file)
        vbox.addLayout(hbox_landmark)
        vbox.addItem(QSpacerItem(300, 10))
        vbox.addWidget(self.model_file)
        vbox.addLayout(hbox_model)
        vbox.addLayout(hbox_load)
        vbox.addWidget(self.quick_help)
        vbox.addStretch()
        vbox.addWidget(self.logo)

        self.setLayout(vbox)
        
        # CSS styling
        with open("GUI/css/left_widget.css", "r") as f:
            self.setStyleSheet(f.read())
        self.load_button.setStyleSheet("background: #4CAF50; color: white")
        self.clear_button.setStyleSheet("background: orange; color: white")
        self.setMaximumWidth(300)

        # Event handler connection
        self.model_file_edit.clicked.connect(self.on_clicking_browse_model)
        self.landmark_file_edit.clicked.connect(self.on_clicking_browse_landmarks)
        self.img_file_edit.clicked.connect(self.on_clicking_browse_images)
        self.brain_button.toggled.connect(self.on_clicking_brain)
        self.cardiac_button.toggled.connect(self.on_clicking_cardiac)
        self.ultrasound_button.toggled.connect(self.on_clicking_ultrasound)
        self.load_button.clicked.connect(self.on_clicking_load)
        self.clear_button.clicked.connect(self.on_clicking_clear)

        # Flag for unit testing
        self.testing = False
    
    def on_clicking_clear(self):
        """
        Handle event when user decide to clear load custom data selection
        """

        if self.window.right_widget.get_mode() == self.window.right_widget.BROWSE_MODE:
            self.window.right_widget.browse_mode.clear_custom_load()
        else:
            self.window.right_widget.automatic_mode.clear_custom_load()
    
    def on_clicking_load(self):
        """
        Handle when user decide to load user default data on browse mode
        """

        # Reset SimpleImageViewer widget
        self.window.right_widget.browse_mode.set_paths()
        self.window.right_widget.browse_mode.load_img()
        self.window.widget.plot_3d.clear_3d()
        self.window.right_widget.browse_mode.plot.clear_2d()
        self.window.widget.cnt_browse = 0

    def on_clicking_brain(self, enabled):
        """
        Handle event when brain button is clicked
        """

        if enabled:
            # If browse mode, change picture
            if self.window.right_widget.get_mode() == self.window.right_widget.BROWSE_MODE:
                # Save HITL status
                self.window.right_widget.save_HITL()
                self.window.right_widget.browse_mode.set_paths()
                self.window.right_widget.browse_mode.load_img()

                # Clear 3d and 2d plot
                self.window.widget.plot_3d.clear_3d()
                self.window.right_widget.browse_mode.plot.clear_2d()

    def on_clicking_ultrasound(self, enabled):
        """
        Handle event when ultrasound button is clicked
        """

        if enabled:
            # If browse mode, change picture
            if self.window.right_widget.get_mode() == self.window.right_widget.BROWSE_MODE:
                # Save HITL status
                self.window.right_widget.save_HITL()
                self.window.right_widget.browse_mode.set_paths()
                self.window.right_widget.browse_mode.load_img()

                # Clear 3d and 2d plot
                self.window.widget.plot_3d.clear_3d()
                self.window.right_widget.browse_mode.plot.clear_2d()

    def on_clicking_cardiac(self, enabled):
        """
        Handle event when brain button is clicked
        """
        if enabled:
            # If browse mode, change picture
            if self.window.right_widget.get_mode() == self.window.right_widget.BROWSE_MODE:
                # Save HITL status
                self.window.right_widget.save_HITL()
                self.window.right_widget.browse_mode.set_paths()
                self.window.right_widget.browse_mode.load_img()

                # Clear 3d and 2d plot
                self.window.widget.plot_3d.clear_3d()
                self.window.right_widget.browse_mode.plot.clear_2d()

    def reset_file_edit_text(self):
        """
        Used to reset file edit text
        """

        self.model_file_edit_text.setText(self.DEFAULT_DATA_NOTIFICATION)
        self.landmark_file_edit_text.setText(self.DEFAULT_DATA_NOTIFICATION)
        self.img_file_edit_text.setText(self.DEFAULT_DATA_NOTIFICATION)

    def on_clicking_browse_model(self):
        """
        Handle when user select to browse model
        """

        # Skip user input if unit-testing
        if self.testing:
            self.fname_model = ('./data/models/DQN_multiscale_brain_mri_point_pc' +
                '_ROI_45_45_45/model-600000.data-00000-of-00001', '')
        else:
            self.fname_model = QFileDialog.getOpenFileName(self, "Browse Model",
                "./data/models/", filter="*.data-*")

        # Set text to label
        filename = self.fname_model[0].split("/")
        self.model_file_edit_text.setText(f"<i> {filename[-1]} </i>")

        # Indicate that user has make a selection
        self.window.right_widget.automatic_mode.fname_model.user_define = True
        self.window.right_widget.automatic_mode.terminal.add_log("blue", f"Load Model: {filename[-1]}")

        # Indicate appropriate path
        self.fname_model = self.fname_model[0]

    def on_clicking_browse_landmarks(self):
        """
        Handle when user select to browse landmarks
        """

        # Skip user input if unit-testing
        if self.testing:
            self.fname_landmarks = ('./data/filenames/brain_test_landmarks_new_paths.txt', '')
        else:
            self.fname_landmarks = QFileDialog.getOpenFileName(self, "Browse Landmark",
                "./data/filenames/local", filter="txt files (*landmark*.txt)")
            
        # Set text to label
        filename = self.fname_landmarks[0].split("/")
        self.landmark_file_edit_text.setText(f"<i> {filename[-1]} </i>")

        # Indicate that user has make a selection (automatic mode)
        self.window.right_widget.automatic_mode.fname_landmarks.user_define = True
        self.window.right_widget.automatic_mode.terminal.add_log("blue", f"Load Landmark: {filename[-1]}")

        # Indicate that user has make a selection (browse mode)
        self.window.right_widget.browse_mode.fname_landmarks.user_define = True

        # Indicate appropriate path
        self.fname_landmarks = self.fname_landmarks[0]

    def on_clicking_browse_images(self):
        """
        Handle when user select to browse images
        """
        # Skip user dialog if unit testing
        if self.testing:
            self.fname_images = ('./data/filenames/brain_test_files_new_paths.txt', '')
        else:
            self.fname_images = QFileDialog.getOpenFileName(self, "Browse Image",
                "./data/filenames/local", filter="txt files (*files*.txt)")

        # Set text to label
        filename = self.fname_images[0].split("/")
        self.img_file_edit_text.setText(f"<i> {filename[-1]} </i>")

        # Indicate that user has make a selection
        self.window.right_widget.automatic_mode.fname_images.user_define = True
        self.window.right_widget.automatic_mode.terminal.add_log("blue", f"Load Image: {filename[-1]}")

        self.window.right_widget.browse_mode.fname_images.user_define = True

        # Indicate appropriate path
        self.fname_images = self.fname_images[0]


################################################################################
## QuickHelp Widget
# Used to display quick help on left side

class QuickHelp(QWidget):

    def __init__(self):
        super().__init__()

        # Initialise text edit
        self.quick_help = QPlainTextEdit()
        self.quick_help.setReadOnly(True)
        self.automatic_mode_help_text()

        # Manage layout
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("<hr />"))
        vbox.addItem(QSpacerItem(300, 20))
        vbox.addWidget(QLabel("Quick Help"))
        vbox.addWidget(self.quick_help)
        self.setLayout(vbox)

        # Stylesheet
        self.quick_help.setStyleSheet("background: white")
    
    def browse_mode_help_text(self):
        """
        Content of browse mode quick help.
        """

        self.quick_help.clear()
        with open("GUI/text/quick_browse_text.html", "r") as f:
            self.quick_help.appendHtml(f.read())
    
    def automatic_mode_help_text(self):
        """
        Content of automatic mode quick help
        """
        self.quick_help.clear()

        with open("GUI/text/quick_automatic_text.html", "r") as f:
            self.quick_help.appendHtml(f.read())

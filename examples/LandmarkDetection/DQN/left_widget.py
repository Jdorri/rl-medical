################################################################################
## Left widget file 
# Author: Maleakhi, Alex, Jamie, Faidon
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
    DEFAULT_DATA_NOTIFICATION = "Default data selected"

    def __init__(self, window):
        super().__init__()
        # Window object to access windows components
        self.window = window # Store window object to enable control over windows functionality
        
        self.title = QLabel("<b> Settings </b>")

        ## Default file mode
        self.simple_title = QLabel("<i> Load Default Data </i>")
        self.brain_button = QRadioButton("Brain")
        self.cardiac_button = QRadioButton("Cardiac")
        self.ultrasound_button = QRadioButton("Fetal")
        self.brain_button.setChecked(True)

        ## Advance file mode
        self.advance_title = QLabel("<i> Load Custom Data </i>")
        # Load model settings
        self.model_file = QLabel('Load Model', self)
        self.model_file_edit = QPushButton('Browse', self)
        self.model_file_edit_text = QLabel(self.DEFAULT_DATA_NOTIFICATION)

        # Load landmark settings
        self.landmark_file = QLabel('Load Landmark', self)
        self.landmark_file_edit = QPushButton('Browse', self)
        self.landmark_file_edit_text = QLabel(self.DEFAULT_DATA_NOTIFICATION)

        # Upload image settings
        self.img_file = QLabel('Upload Image', self)
        self.img_file_edit = QPushButton('Browse', self)
        self.img_file_edit_text = QLabel(self.DEFAULT_DATA_NOTIFICATION)

        # Logo settings
        self.logo = QLabel()
        pixmap_logo = QPixmap("./images/imperial_logo.png")
        pixmap_logo = pixmap_logo.scaledToHeight(50)
        self.logo.setPixmap(pixmap_logo)
        
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
        vbox.addItem(QSpacerItem(300, 20))
        vbox.addWidget(self.landmark_file)
        vbox.addLayout(hbox_landmark)
        vbox.addItem(QSpacerItem(300, 20))
        vbox.addWidget(self.model_file)
        vbox.addLayout(hbox_model)
        vbox.addStretch()
        vbox.addWidget(self.logo)

        self.setLayout(vbox)

        # CSS styling
        self.setStyleSheet("""
            QPushButton {
                background: #006EAF; 
                color: white
            }

            QFrame, QRadioButton {
                background: #EBEEEE;
            }
            """)

        # Event handler connection
        self.model_file_edit.clicked.connect(self.on_clicking_browse_model)
        self.landmark_file_edit.clicked.connect(self.on_clicking_browse_landmarks)
        self.img_file_edit.clicked.connect(self.on_clicking_browse_images)
        self.brain_button.toggled.connect(self.on_clicking_brain)
        self.cardiac_button.toggled.connect(self.on_clicking_cardiac)
        self.ultrasound_button.toggled.connect(self.on_clicking_ultrasound)

        self.testing = False
    

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
                self.window.right_widget.browse_mode.window.widget.clear_3d()
                self.window.right_widget.browse_mode.terminal_duplicate.appendHtml(f"<b><p style='color:blue'> &#36; Load BrainMRI </p></b>")        
    
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
                self.window.right_widget.browse_mode.window.widget.clear_3d()
                self.window.right_widget.browse_mode.terminal_duplicate.appendHtml(f"<b><p style='color:blue'> &#36; Load FetalUS </p></b>")        

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
                self.window.right_widget.browse_mode.window.widget.clear_3d()
                self.window.right_widget.browse_mode.terminal_duplicate.appendHtml(f"<b><p style='color:blue'> &#36; Load CardiacMRI </p></b>")        

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
        if not self.testing:
            self.fname_model = QFileDialog.getOpenFileName(self, "Browse Model",
                "./data/models/", filter="*.data-*")
            # Set text to label
            filename = self.fname_model[0].split("/")
            self.model_file_edit_text.setText(filename[-1])

            # Indicate that user has make a selection
            self.window.right_widget.automatic_mode.fname_model.user_define = True
            self.window.right_widget.automatic_mode.terminal.appendHtml(f"<b><p style='color:blue'> &#36; Load Model: {filename[-1]} </p></b>")

            # Indicate appropriate path
            self.fname_model = "./data/models/" + filename[-2] + "/" + filename[-1]

    def on_clicking_browse_landmarks(self):
        """
        Handle when user select to browse landmarks
        """
        if not self.testing:
            self.fname_landmarks = QFileDialog.getOpenFileName(self, "Browse Landmark",
                "./data/filenames", filter="txt files (*landmark*.txt)")
            # Set text to label
            filename = self.fname_landmarks[0].split("/")
            self.landmark_file_edit_text.setText(filename[-1])

            # Indicate that user has make a selection
            self.window.right_widget.automatic_mode.fname_landmarks.user_define = True
            self.window.right_widget.automatic_mode.terminal.appendHtml(f"<b><p style='color:blue'> &#36; Load Landmark: {filename[-1]} </p></b>")

            # Indicate appropriate path
            self.fname_landmarks = "./data/filenames/" + filename[-1]

    def on_clicking_browse_images(self):
        """
        Handle when user select to browse images
        """
        if not self.testing:
            self.fname_images = QFileDialog.getOpenFileName(self, "Browse Image",
                "./data/filenames/local/", filter="txt files (*train_files*.txt)")
            # Set text to label
            filename = self.fname_images[0].split("/")
            self.img_file_edit_text.setText(filename[-1])

            # Indicate that user has make a selection
            self.window.right_widget.automatic_mode.fname_images.user_define = True
            self.window.right_widget.automatic_mode.terminal.appendHtml(f"<b><p style='color:blue'> &#36; Load Image: {filename[-1]} </p></b>")

            # Indicate appropriate path
            self.fname_images = "./data/filenames/local/" + filename[-1]
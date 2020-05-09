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
        self.setMaximumWidth(350)
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

        # Load button (HITL mode)
        self.load_button = QPushButton("Load", self)
        self.load_button.hide()
        
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
        hbox_load.addWidget(self.load_button)
        hbox_load.addWidget(QLabel(""))

        self.quick_help = QPlainTextEdit()
        self.quick_help.setReadOnly(True)

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
        vbox.addLayout(hbox_load)
        vbox.addWidget(QLabel("<hr />"))
        vbox.addWidget(QLabel("<i> Quick Help </i>"))
        vbox.addWidget(self.quick_help)
        vbox.addStretch()
        vbox.addWidget(self.logo)

        self.setLayout(vbox)
        
        self.automatic_mode_help_text()
        
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
        self.load_button.setStyleSheet("background: #4CAF50")
        self.quick_help.setStyleSheet("background: white")

        # Event handler connection
        self.model_file_edit.clicked.connect(self.on_clicking_browse_model)
        self.landmark_file_edit.clicked.connect(self.on_clicking_browse_landmarks)
        self.img_file_edit.clicked.connect(self.on_clicking_browse_images)
        self.brain_button.toggled.connect(self.on_clicking_brain)
        self.cardiac_button.toggled.connect(self.on_clicking_cardiac)
        self.ultrasound_button.toggled.connect(self.on_clicking_ultrasound)
        self.load_button.clicked.connect(self.on_clicking_load)

        self.testing = False
    
    def browse_mode_help_text(self):
        self.quick_help.clear()
        self.quick_help.appendHtml("""
        <b><p style='color:#003E74'>Browse Mode</p></b>
        <p style='color:#006EAF'><i>(For more information: Ctrl+H)</i></p><br />

        <br /><b>1. Load data:</b> choose default or browse custom data.
        <br /><b>2. Enable HITL:</b> toggle checkbox to notify to store user interaction data.
        <br /><b>3. Navigation:</b> press <i>Human Actions</i> arrow to navigate agent until Error = 0.
        <br /><b>4. Next Image:</b> press next image to annotate next sequence of image.
        <br /><b>5. Save data:</b> toggle off <i>Enable HITL</i> checkbox or close GUI to save user interaction.
        """)
    
    def automatic_mode_help_text(self):
        self.quick_help.clear()
        self.quick_help.appendHtml("""
        <b><p style='color:#003E74'>Automatic Mode</p></b>
        <p style='color:#006EAF'><i>For more information: Ctrl+H</i></p><br />

        <br /><b>1. Load data:</b> choose default or browse custom data.
        <br /><b>2. Task selection: </b>select (Play|Evaluation) task.
        <br /><b>3. Simulation: </b>start visualisation by pressing <i>Start</i> button, <i>Pause</i> to pause simulation
        , <i>Terminate</i> to terminate simulation. After termination, you can run a new simulation using different settings.
        <br /><b>4. Agent speed:</b> optionally change simulation speed using agent speed slider.
        """)
    
    def on_clicking_load(self):
        """
        Handle when user decide to load user default data on browse mode
        """
        # Reset SimpleImageViewer widget
        self.window.right_widget.browse_mode.set_paths()
        self.window.right_widget.browse_mode.load_img()
        self.window.widget.clear_3d()
        self.window.widget.set_3d_axes(self.window.widget.ax, \
                self.window.widget.width, self.window.widget.height, \
                self.window.widget.height_x)
        self.window.widget.canvas.draw()

    def on_clicking_brain(self, enabled):
        """
        Handle event when brain button is clicked
        """
        if enabled:
            # If browse mode, change picture
            if self.window.right_widget.get_mode() == self.window.right_widget.BROWSE_MODE:
                # Save HITL status
                self.window.right_widget.save_HITL()
                # self.window.widget.change_layout("BrainMRI")
                self.window.right_widget.browse_mode.set_paths()
                self.window.right_widget.browse_mode.load_img()
                self.window.right_widget.browse_mode.window.widget.clear_3d()
                self.window.right_widget.browse_mode.terminal_duplicate.appendHtml(
                    f"<b><p style='color:blue'> &#36; Load BrainMRI </p></b>")        

                self.window.widget.set_3d_axes(self.window.widget.ax, \
                        self.window.widget.width, self.window.widget.height, \
                        self.window.widget.height_x)
                self.window.widget.canvas.draw()

    def on_clicking_ultrasound(self, enabled):
        """
        Handle event when ultrasound button is clicked
        """
        if enabled:
            # If browse mode, change picture
            if self.window.right_widget.get_mode() == self.window.right_widget.BROWSE_MODE:
                # Save HITL status
                self.window.right_widget.save_HITL()
                # self.window.widget.change_layout("FetalUS")
                self.window.right_widget.browse_mode.set_paths()
                self.window.right_widget.browse_mode.load_img()
                self.window.right_widget.browse_mode.window.widget.clear_3d()
                self.window.right_widget.browse_mode.terminal_duplicate.appendHtml(
                    f"<b><p style='color:blue'> &#36; Load FetalUS </p></b>")        

                self.window.widget.set_3d_axes(self.window.widget.ax, \
                        self.window.widget.width, self.window.widget.height, \
                        self.window.widget.height_x)
                self.window.widget.canvas.draw()

    def on_clicking_cardiac(self, enabled):
        """
        Handle event when brain button is clicked
        """
        if enabled:
            # If browse mode, change picture
            if self.window.right_widget.get_mode() == self.window.right_widget.BROWSE_MODE:
                # Save HITL status
                self.window.right_widget.save_HITL()
                # self.window.widget.change_layout("CardiacMRI")
                self.window.right_widget.browse_mode.set_paths()
                self.window.right_widget.browse_mode.load_img()
                self.window.right_widget.browse_mode.window.widget.clear_3d()
                self.window.right_widget.browse_mode.terminal_duplicate.appendHtml(
                    f"<b><p style='color:blue'> &#36; Load CardiacMRI </p></b>")        

                self.window.widget.set_3d_axes(self.window.widget.ax, \
                        self.window.widget.width, self.window.widget.height, \
                        self.window.widget.height_x)
                self.window.widget.canvas.draw()

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
        self.model_file_edit_text.setText(filename[-1])

        # Indicate that user has make a selection
        self.window.right_widget.automatic_mode.fname_model.user_define = True
        self.window.right_widget.automatic_mode.terminal.appendHtml(
            f"<b><p style='color:blue'> &#36; Load Model: {filename[-1]} </p></b>")

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
                "./data/filenames", filter="txt files (*landmark*.txt)")
            
        # Set text to label
        filename = self.fname_landmarks[0].split("/")
        self.landmark_file_edit_text.setText(filename[-1])

        # Indicate that user has make a selection
        self.window.right_widget.automatic_mode.fname_landmarks.user_define = True
        self.window.right_widget.automatic_mode.terminal.appendHtml(
            f"<b><p style='color:blue'> &#36; Load Landmark: {filename[-1]} </p></b>")

        # Indicate that user has make a selection (browse mode)
        self.window.right_widget.browse_mode.fname_landmarks.user_define = True
        self.window.right_widget.browse_mode.terminal_duplicate.appendHtml(
            f"<b><p style='color:blue'> &#36; Load Landmark: {filename[-1]} </p></b>")

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
                "./data/filenames")

        # Set text to label
        filename = self.fname_images[0].split("/")
        self.img_file_edit_text.setText(filename[-1])

        # Indicate that user has make a selection
        self.window.right_widget.automatic_mode.fname_images.user_define = True
        self.window.right_widget.automatic_mode.terminal.appendHtml(
            f"<b><p style='color:blue'> &#36; Load Image: {filename[-1]} </p></b>")

        self.window.right_widget.browse_mode.fname_images.user_define = True
        self.window.right_widget.browse_mode.terminal_duplicate.appendHtml(
            f"<b><p style='color:blue'> &#36; Load Image: {filename[-1]} </p></b>")

        # Indicate appropriate path
        self.fname_images = self.fname_images[0]
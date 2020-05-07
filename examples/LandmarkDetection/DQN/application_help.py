import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ApplicationHelp(QWidget):

    def __init__(self):
        super(ApplicationHelp, self).__init__()
        # Close help window with shortcut
        self.shortcut_close = QShortcut(QKeySequence('Ctrl+Q'), self)
        self.shortcut_close.activated.connect(self.close)
	    
        ## Left settings on help window
        self.leftlist = QListWidget()
        self.leftlist.insertItem(0, 'Welcome')
        self.leftlist.insertItem(1, 'Automatic Mode')
        self.leftlist.insertItem(2, 'Browse Mode')

        # Initialise respective widgets
        self.welcome_stack = QWidget()
        self.automatic_stack = QWidget()
        self.browse_stack = QWidget()

        self.welcome_UI()
        self.automatic_UI()
        self.browse_UI()
		
        # Stack (tabbing)
        self.Stack = QStackedWidget(self)
        self.Stack.addWidget(self.welcome_stack)
        self.Stack.addWidget(self.automatic_stack)
        self.Stack.addWidget(self.browse_stack)

        # Manage overall widget layout
        hbox = QHBoxLayout(self)
        hbox.addWidget(self.leftlist)
        hbox.addWidget(self.Stack)
        self.setLayout(hbox)

        # Event handler
        self.leftlist.currentRowChanged.connect(self.display)

        # Responsive design tools
        self.leftlist.setMaximumWidth(300)
        self.resize(1000, 800)
        self.center()
        self.setWindowTitle('Application Help')
        
        self.setStyleSheet("""
        QWidget {
            background: white;
        }
        QListWidget {
            background: #EBEEEE;
            font-size: 14px;
            padding: 5px;
        }
        QPlainTextEdit {
            border: none;
        }
        """)
    
    def center(self):
        """
        Force widget to be on the center
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
		
    def welcome_UI(self):
        self.welcome_text = QPlainTextEdit(self)
        self.welcome_text.setReadOnly(True)
        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(self.welcome_text)

        self.welcome_text.appendHtml("""
        <h1 style='color:#003E74'> Welcome! </h1>
        <br />
        <p>Welcome to <b>RL Medical GUI</b>! Reinforcement Learning (RL) Medical GUI is a GUI application for finding established standard views 
        and landmarks in the image (for <i>Brain</i>, <i>Cardiac</i>, and <i>Fetal</i>). The GUI has two main features: 
        (1) visualisation of trained agent's trajectories, (2) platform for collecting data (user interaction) 
        for Human-in-the-loop (HITL) experiments.</p><br /> 

        <h2 style='color:#009CBC'>Application Modes</h2>
        <br />
        <ul>
            <li><b>- Automatic Mode:</b> allow visualisation of trained agent's trajectories.</li>
            <li><b>- Browse Mode:</b> allow simple user interaction with RL agent, enabling collection of data for HITL experiments.</li>
        </ul>

        <br />
        <p><b>Notes:</b> For more information about installation, problem specification, and paper references, please visit <a href="https://github.com/ollenilsson19/rl-medical">https://github.com/ollenilsson19/rl-medical</a></p>
        """)

        self.welcome_stack.setLayout(hbox_layout)

    def automatic_UI(self):
        self.automatic_text = QPlainTextEdit(self)
        self.automatic_text.setReadOnly(True)
        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(self.automatic_text)

        self.automatic_text.appendHtml("""
        <h1 style='color:#003E74'> Automatic Mode Help </h1>
        <br />
        <p>Automatic mode allows <i>axial</i>, <i>coronal</i>, <i>sagittal</i> 
        , and <i>3D</i> visualisation of trained agent's trajectories.</p> <br />

        <h2 style='color:#009CBC'>How to Run Simulation?</h2><br />
        <ol>
            <li><b>1. Load Data</b>: There are two options to load the data: <i>default</i> and
            <i>custom</i>. To load default data, simply toggle the appropriate radio button (i.e. Brain|Cardiac|Fetal). This will 
            prepare default model, image, and landmark for the selected use-case. You can also load custom data by uploading your own image, landmark, and model files
            through <i>Browse</i> buttons. Please ensure that you select the correct combination of files.</li>
            <li><b>2. Task Selection</b>: Select either <i>Play</i> or <i>Evaluation</i> task before running the code.</li>
            <li><b>3. Simulation</b>: Press <i>Start</i> button to start simulation, <i>Pause</i> to pause simulation, and <i>Terminate</i> to exit simulation. After termination, you can
            then follow step 1 and 2 to run new simulation.</li>
            <li><b>4. Agent Speed</b>: You can optionally change simulation speed using the agent speed slider.</li>
        </ol>
        """)

        self.automatic_stack.setLayout(hbox_layout)
		
    def browse_UI(self):
        self.browse_text = QPlainTextEdit(self)
        self.browse_text.setReadOnly(True)
        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(self.browse_text)

        self.browse_text.appendHtml("""
        <h1 style='color:#003E74'> Browse Mode Help </h1>
        <br />
        <p>Browse mode allows simple user interaction with RL agent, enabling collection of data for HITL experiments.
        </p><br />

        <h2 style='color:#009CBC'>How to Gather Human-in-the-Loop Data?</h2><br />
        <b>1. Load Data</b>: There are two options to load the data: <i>default</i> and
            <i>custom</i>. To load default data, simply toggle the appropriate radio button (i.e. Brain|Cardiac|Fetal). This will 
            prepare default image and landmark for the selected use-case. You can also load custom data by uploading your own image and landmark files
            through <i>Browse</i> buttons. Then press <i>Load</i> to display your files. Please ensure that you select the correct combination of files.
        <br /><b>2. Enable HITL</b> To notify that you want to store HITL data, toggle <i>Enable HITL</i> checkbox. After toggling the checkbox, data (user-interaction)
        will be stored on appropriate pickle file.
        <br /><b>3. Navigating in HITL mode</b> The task is to move agent towards the target (red dot). 
        Press <i>Human Actions</i> arrows to navigate until you reach the red dot (Error ~ 0.0). You can control step size
         using the <i>-</i> and <i>+</i> buttons to reduce or increase step size.
        <br /><b>4. Next Image</b> Press next image to annotate next sequence of image. Alternatively, you can delete previous annotation by clicking <i>Delete Episode</i>.
        <br /><b>5. Save data</b>  Once finished, to save the HITL session, either: (1) close the GUI or (2) click on <i>Enable HITL</i> checkbox again (it will
         automatically save a pickle file in /data/HITL).
        """)


        self.browse_stack.setLayout(hbox_layout)
		
    def display(self,i):
        self.Stack.setCurrentIndex(i)
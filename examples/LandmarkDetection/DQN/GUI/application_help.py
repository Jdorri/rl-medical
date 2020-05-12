################################################################################
## PyQt thread files containing codes for implementing multithreading on GUI.
# Author: Maleakhi, Alex, Faidon, Jamie, Olle, Harry
################################################################################

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


################################################################################
## ApplicationHelp
# Help window widgets

class ApplicationHelp(QWidget):
    """
    Widget class containing data and formatting of help window.
    """

    def __init__(self):
        super(ApplicationHelp, self).__init__()
        
        # Shortcut to close help window
        self.shortcut_close = QShortcut(QKeySequence('Ctrl+Q'), self)
        self.shortcut_close.activated.connect(self.close)
	    
        # Left part of help window
        self.leftlist = QListWidget()
        self.leftlist.insertItem(0, 'Welcome')
        self.leftlist.insertItem(1, 'Automatic Mode')
        self.leftlist.insertItem(2, 'Browse Mode')

        # Initialise respective widgets
        self.welcome_stack = QWidget()
        self.automatic_stack = QWidget()
        self.browse_stack = QWidget()

        # Initialise UI layout and elements
        self.welcome_UI()
        self.automatic_UI()
        self.browse_UI()
		
        # Right part of help window
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

        # Responsive design 
        self.leftlist.setMaximumWidth(300)
        self.resize(800, 600)
        self.center()
        self.setWindowTitle('Application Help')
        
        # Manage GUI styling
        with open("GUI/css/application_help.css", "r") as f:
            self.setStyleSheet(f.read())
    
    def center(self):
        """
        Force widget to be on the center of desktop
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
		
    def welcome_UI(self):
        """
        Manage welcome layout and content.
        """

        # Welcome text widget
        self.welcome_text = QPlainTextEdit(self)
        self.welcome_text.setReadOnly(True)
        
        # Add widget to layout
        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(self.welcome_text)
        self.welcome_stack.setLayout(hbox_layout)

        # Welcome text content
        with open("GUI/text/welcome_text.html", "r") as f:
            self.welcome_text.appendHtml(f.read())


    def automatic_UI(self):
        """
        Manage automatic mode help layout and content
        """

        # Automatic text widget
        self.automatic_text = QPlainTextEdit(self)
        self.automatic_text.setReadOnly(True)
        
        # Add widget to layout
        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(self.automatic_text)
        self.automatic_stack.setLayout(hbox_layout)

        # Help text content
        with open("GUI/text/automatic_text.html") as f:
            self.automatic_text.appendHtml(f.read())
		
    def browse_UI(self):
        """
        Manage browse mode help layout and content
        """

        # Browse text widget
        self.browse_text = QPlainTextEdit(self)
        self.browse_text.setReadOnly(True)

        # Add widget to layout
        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(self.browse_text)
        self.browse_stack.setLayout(hbox_layout)

        # Help text content
        with open("GUI/text/browse_text.html") as f:
            self.browse_text.appendHtml(f.read())

    def display(self,i):
        """
        Event handler for stack.

        :param i: index of active stack
        """
        
        self.Stack.setCurrentIndex(i)
################################################################################
## Terminal Widget
# Author: Maleakhi, Alex, Faidon, Jamie, Olle, Harry
################################################################################

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


###############################################################################
## Terminal (Automatic Mode)
# For logging automatic mode

class Terminal(QWidget):
    """
    Class to log commands and other relevant simulation details.
    """

    def __init__(self):

        super().__init__()

        # Terminal log
        self.terminal = QPlainTextEdit(self)
        self.terminal.setReadOnly(True)

        # Widget layout
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("<hr />"))
        vbox.addItem(QSpacerItem(300, 20)) # spacer
        vbox.addWidget(QLabel("Logs"))
        vbox.addWidget(self.terminal)

        self.setLayout(vbox)
    
    def terminal_signal_handler(self, current_episode, total_episode, score, 
                                    distance_error, q_values):
        """
        When an episode ends, terminal needs to log details.

        :param current_episode: current episode (int)
        :param total_episode: total episodes that will be run
        :param score: score reach at the end of an episode
        :param distance_error: final error
        :param q_values: final q_values
        """

        # HTML value
        self.terminal.appendHtml(
            f"<b> Episode {current_episode}/{total_episode} </b>"
        )

        self.terminal.appendHtml(
            f"<i>Score:</i> {score}"
        )

        self.terminal.appendHtml(
            f"<i>Distance Error:</i> {distance_error}"
        )

        self.terminal.appendHtml(
            f"<i>Q Values:</i> {q_values} <hr />"
        )
    
    def add_log(self, color, log):
        """
        Appending command to terminal

        :param color: color in either hex numbers, rgb, or string
        :param log: message to be appended to terminal
        """

        message = f"<b><p style='color:{color}'> &#36; {log}</p></b>"
        self.terminal.appendHtml(message)
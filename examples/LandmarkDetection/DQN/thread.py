################################################################################
## PyQt thread files containing codes for QThread
# Author: Maleakhi, Alex, Faidon, Jamie
# Credit: Code adapted from Amir Alansary viewer.py file
################################################################################

from threading import Thread

################################################################################
## Main Thread Class

class WorkerThread(Thread):
    def __init__(self, target_function):
        super().__init__(daemon=True)
        self.target_function = target_function

    def run(self):
        self.target_function()

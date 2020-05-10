################################################################################
## PyQt thread files containing codes for implementing multithreading on GUI.
# Author: Maleakhi, Alex, Faidon, Jamie, Olle, Harry
################################################################################

from threading import Thread, Event


################################################################################
## Main Thread Class

class WorkerThread(Thread):
    """
    Thread class which will be used to instantiate thread for RL agent simulation.
    """

    # Indicate sleep time for thread controlling simulation speed
    FAST = 1
    MEDIUM = 0
    SLOW = -1

    def __init__(self, target_function):
        """
        Thread constructor.

        :param target_function: function which will be executed on the thread.
        """

        super().__init__(daemon=True)
        
        self.terminate = False # flag indicate to early kill thread
        self.target_function = target_function
        self.pause = False # flag indicating to pause simulation (pause thread function)
        self.speed = WorkerThread.FAST # indicate simulation/ agent speed
        self.window = None # store window (main gui element)

    def run(self):
        """
        Run the thread.
        """

        self.target_function()

        # Restart GUI after successfully run target_function.
        self.window.right_widget.automatic_mode.restart()
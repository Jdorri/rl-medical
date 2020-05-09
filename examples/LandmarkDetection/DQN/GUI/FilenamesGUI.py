################################################################################
## Manage load custom data.
# Author: Maleakhi, Alex, Faidon, Jamie, Olle, Harry
################################################################################


###############################################################################
## FilenamesGUI
# Used to store file path

class FilenamesGUI:
    """
    Store file path string + book keepings.
    """

    def __init__(self):
        self.user_define = False # indication whether user has load anything
        self.name = "" # name of the file
    
    @staticmethod
    def copy(file1, file2):
        """
        Copy file 1 to file 2.

        :param file1: FilenamesGUI instance
        :param file2: FilenamesGUI instance
        """
        file2.name = file1.name
        file2.user_define = file1.user_define
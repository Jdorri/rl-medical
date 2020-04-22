################################################################################
## Class representing GUI files containers for model, landmark, and image
# Author: Maleakhi, Alex, Faidon, Jamie
################################################################################


###############################################################################
## FilenamesGUI
# Used to store file path

class FilenamesGUI:
    def __init__(self):
        self.user_define = False # indication whether user has load anything
        self.name = "" # name of the file
    
    @staticmethod
    def copy(file1, file2):
        """
        Copy file 1 to file 2
        """
        file2.name = file1.name
        file2.user_define = file1.user_define
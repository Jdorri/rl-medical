import sys
from PyQt5.QtWidgets import*
from PyQt5.QtCore import Qt, pyqtSlot

# custom class
class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # window title
        self.setWindowTitle('Anatomical Landmark Detection')

        # initialise labels
        self.GPU = QLabel('GPU', self)
        self.load = QLabel('Load Model', self)
        self.task = QLabel('Task', self)
        self.algorithm = QLabel('Algorithm', self)
        self.file1 = QLabel('File 1: Images', self)
        self.file2 = QLabel('File 2: Landmarks', self)
        self.GIF = QLabel('Save GIF', self)
        self.video = QLabel('Save Video', self)
        self.log_dir = QLabel('Store Logs', self)
        self.name = QLabel('Experiment Name', self)

        # initialise widgets
        self.GPU_edit = QLineEdit()
        self.load_edit = QPushButton('Browse', self)
        self.task_edit = QComboBox()
        self.algorithm_edit = QComboBox()
        self.file1_edit = QPushButton('Browse', self)
        self.file2_edit = QPushButton('Browse', self)
        self.GIF_edit =  QCheckBox()
        self.video_edit = QCheckBox()
        self.log_dir_edit = QPushButton('Browse', self)
        self.name_edit = QLineEdit()
        self.run = QPushButton('Run', self)
        self.exit = QPushButton('Exit', self)

        # add widget functionality
        self.task_edit.addItems(['Play', 'Evaluation', 'Train'])
        self.algorithm_edit.addItems(['DQN', 'Double', 'Dueling', 'Dueling Double'])

        # initialise grid/set spacing
        grid = QGridLayout()
        grid.setSpacing(10)

        # add widgets to grid
        grid.addWidget(self.task, 1, 0)
        grid.addWidget(self.task_edit, 1, 1)

        grid.addWidget(self.algorithm, 2, 0)
        grid.addWidget(self.algorithm_edit, 2, 1)

        grid.addWidget(self.load, 3, 0)
        grid.addWidget(self.load_edit, 3, 1)

        grid.addWidget(self.GPU, 4, 0)
        grid.addWidget(self.GPU_edit, 4, 1)

        grid.addWidget(self.file1, 5, 0)
        grid.addWidget(self.file1_edit, 5, 1)

        grid.addWidget(self.file2, 6, 0)
        grid.addWidget(self.file2_edit, 6, 1)

        grid.addWidget(self.GIF, 7, 0)
        grid.addWidget(self.GIF_edit, 7, 1)

        grid.addWidget(self.video, 8, 0)
        grid.addWidget(self.video_edit, 8, 1)

        grid.addWidget(self.log_dir, 9, 0)
        grid.addWidget(self.log_dir_edit, 9, 1)

        grid.addWidget(self.name, 10, 0)
        grid.addWidget(self.name_edit, 10, 1)

        grid.addWidget(self.run, 11, 0)
        grid.addWidget(self.exit, 12, 0)

        self.setLayout(grid)
        self.setGeometry(100, 100, 350, 400)

        # connections
        self.load_edit.clicked.connect(self.on_clicking_browse1)
        self.file1_edit.clicked.connect(self.on_clicking_browse2)
        self.file2_edit.clicked.connect(self.on_clicking_browse3)
        self.log_dir_edit.clicked.connect(self.on_clicking_browse4)
        self.run.clicked.connect(self.on_clicking_run)
        self.exit.clicked.connect(self.close_it)

        self.show()

    @pyqtSlot()
    def on_clicking_run(self):
        GPU_value = self.GPU_edit.text()
        DQN_variant_value = self.algorithm_edit.currentText()
        task_value = self.task_edit.currentText()
        GIF_value = self.GIF_edit.isChecked()
        video_value = self.video_edit.isChecked()
        load_value = self.load_edit.isChecked()
        name_value = self.name_edit.text()

    @pyqtSlot()
    def on_clicking_browse1(self):
        file_name1 = QFileDialog.getOpenFileName()

    @pyqtSlot()
    def on_clicking_browse2(self):
        file_name2 = QFileDialog.getOpenFileName()

    @pyqtSlot()
    def on_clicking_browse3(self):
        file_name3 = QFileDialog.getOpenFileName()

    @pyqtSlot()
    def on_clicking_browse4(self):
        file_name4 = QFileDialog.getOpenFileName()

    @pyqtSlot()
    def close_it(self):
        self.close()

# QApplication instance
app = QApplication(sys.argv)

# custom class instance
window = MainWindow()

app.exec_()

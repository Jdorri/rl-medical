import sys
import unittest
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from thread import WorkerThread
from functioning_UI_PyQt import run

class RightWidgetTester(unittest.TestCase):
    '''
    Class to perform unit tests on the buttons within the right widget of the
    GUI Launcher.

    * NOTE * These are tests only for functionality of the GUI. They do not
    test the event signal causes the correct action.

    To run these tests run the following command from the command line
    when in the DQN folder:
    - python -m tests.unit_tests.runner
    '''

    def setUp(self):
        '''Method run before every test. Use this to prepare the test fixture.'''
        self.app, window = run()
        self.w = window.right_widget
        self.w.test_mode = True

    def tearDown(self):
        '''Method run after each test is run. Use this to reset the testing
        environment.'''
        self.w.close()
        self.app.quit()
        self.app, self.w = None, None

    def test_taskComboBox(self):
        # Check default
        self.assertEqual(self.w.task_edit.itemText(self.w.task_edit.currentIndex()), 'Play')
        # Change value and check new
        self.w.task_edit.setCurrentIndex(2)
        self.assertEqual(self.w.task_edit.itemText(self.w.task_edit.currentIndex()), 'Train')

    def test_algorithmComboBox(self):
        # Check default
        self.assertEqual(self.w.algorithm_edit.itemText(self.w.algorithm_edit.currentIndex()), 'DQN')
        # Change value and check new
        self.w.algorithm_edit.setCurrentIndex(2)
        self.assertEqual(self.w.algorithm_edit.itemText(self.w.algorithm_edit.currentIndex()), 'Dueling')

    def test_exitButton(self):
        QTest.mouseClick(self.w.exit, Qt.LeftButton)
        self.assertTrue(self.w.test_click)

    def test_runButton(self):
        QTest.mouseClick(self.w.run, Qt.LeftButton)
        self.assertTrue(self.w.test_click)

    def test_browseImgsButton(self):
        QTest.mouseClick(self.w.img_file_edit, Qt.LeftButton)
        self.assertTrue(self.w.test_click)

    def test_browseModelsButton(self):
        QTest.mouseClick(self.w.load_edit, Qt.LeftButton)
        self.assertTrue(self.w.test_click)

    def test_browseLandmarksButton(self):
        QTest.mouseClick(self.w.landmark_file_edit, Qt.LeftButton)
        self.assertTrue(self.w.test_click)

    def test_browseLogsButton(self):
        QTest.mouseClick(self.w.log_dir_edit, Qt.LeftButton)
        self.assertTrue(self.w.test_click)

    # def test_GIFCheckBox(self):
    #     QTest.mouseClick(self.w.GIF_edit, Qt.LeftButton)
    #     self.assertTrue(self.w.GIF_edit.isChecked(),
    #         pos=QtCore.QPoint(2,self.w.GIF_edit.height()/2))
    #
    # def test_videoCheckBox(self):
    #     QTest.mouseClick(self.w.video_edit, Qt.LeftButton)
    #     self.assertTrue(self.w.test_click)


class LeftWidgetTester(unittest.TestCase):
    '''Same as above but for the left widget'''
    def setUp(self):
        '''Method run before every test. Use this to prepare the test fixture.'''
        self.app, window = run()
        self.w = window.left_widget
        self.w.test_mode = True

    def tearDown(self):
        '''Method run after each test is run. Use this to reset the testing
        environment.'''
        self.w.close()
        self.app.quit()
        self.app, self.w = None, None

    def test_startButton(self):
        QTest.mouseClick(self.w.run_button, Qt.LeftButton)
        self.assertTrue(self.w.test_click)

    def test_agentSpeedSlider(self):
        '''Checks if the slider works and if it adjusts the thread speed'''
        # Check initial position is correct
        self.slider_checker()

        # Change to min value
        self.w.speed_slider.setValue(self.w.speed_slider.minimum())
        self.assertEqual(self.w.speed_slider.value(), self.w.speed_slider.minimum())
        self.slider_checker()

        # Change to medium value
        self.w.speed_slider.setValue(round((self.w.speed_slider.maximum() - \
            self.w.speed_slider.minimum()) / 2, 1) )
        self.slider_checker()

    def slider_checker(self):
        '''Helper function for checking slider position corresponds to correct
        thread speed'''
        if self.w.speed_slider.value() == self.w.speed_slider.maximum():
            self.assertEqual(self.w.thread.speed, WorkerThread.FAST)
        elif self.w.speed_slider.value() == self.w.speed_slider.minimum():
            self.assertEqual(self.w.thread.speed, WorkerThread.SLOW)
        else:
            self.assertEqual(self.w.thread.speed, WorkerThread.MEDIUM)


if __name__ == '__main__':
    unittest.main()

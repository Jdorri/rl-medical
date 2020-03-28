import sys
import unittest
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from thread import WorkerThread
from functioning_UI_PyQt import run

class GUILauncherTester(unittest.TestCase):
    '''
    Class to perform unit tests on the buttons within the GUI Launcher.
    * NOTE * These are tests only for functionality of the GUI. They do not
    test the event signal causes the correct action.

    To run these tests run the following command from the command line
    when in the DQN folder:
    - python -m tests.unit_tests.launcher_tests
    '''

    def setUp(self):
        '''Method run before every test. Use this to init the testing
        environment.'''
        self.app, self.window = run()

    def tearDown(self):
        '''Method run after each test is run. Use this to reset the testing
        environment.'''
        self.window.close()
        self.app.quit()
        self.app, self.window = None, None

    def test_exitButton(self):
        self.window.right_widget.test_mode = True
        QTest.mouseClick(self.window.right_widget.exit, Qt.LeftButton)
        self.assertEqual(True, self.window.right_widget.test_click)

    def test_runButton(self):
        self.window.right_widget.test_mode = True
        QTest.mouseClick(self.window.right_widget.run, Qt.LeftButton)
        self.assertEqual(True, self.window.right_widget.test_click)

    def test_startButton(self):
        self.window.left_widget.test_mode = True
        QTest.mouseClick(self.window.left_widget.run_button, Qt.LeftButton)
        self.assertEqual(True, self.window.left_widget.test_click)

    def test_agentSpeedSlider(self):
        '''Checks if the slider works and if it adjusts the thread speed'''
        self.window.left_widget.test_mode = True
        # Check initial position is correct
        self.slider_checker()

        # Change to min value
        self.window.left_widget.speed_slider.setValue(
            self.window.left_widget.speed_slider.minimum())
        self.assertEqual(self.window.left_widget.speed_slider.value(),
            self.window.left_widget.speed_slider.minimum())
        self.slider_checker()

        # Change to medium value
        self.window.left_widget.speed_slider.setValue(
            round((self.window.left_widget.speed_slider.maximum() - \
            self.window.left_widget.speed_slider.minimum()) / 2, 1) )
        self.slider_checker()

    def slider_checker(self):
        '''Helper function for checking slider position corresponds to correct
        thread speed'''
        if self.window.left_widget.speed_slider.value() == \
                self.window.left_widget.speed_slider.maximum():
            self.assertEqual(self.window.left_widget.thread.speed, WorkerThread.FAST)
        elif self.window.left_widget.speed_slider.value() == \
                self.window.left_widget.speed_slider.minimum():
            self.assertEqual(self.window.left_widget.thread.speed, WorkerThread.SLOW)
        else:
            self.assertEqual(self.window.left_widget.thread.speed, WorkerThread.MEDIUM)


if __name__ == '__main__':
    unittest.main()

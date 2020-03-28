import sys
import unittest
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from functioning_UI_PyQt import run

class GUILauncherTester(unittest.TestCase):
    '''
    Class to perform unit tests on the buttons within the GUI Launcher.
    * NOTE * These are tests only for functionality of the GUI. They do not
    test the event signal causes the correct action.
    '''

    def setUp(self):
        '''
        Method run before every test. Use this to init the testing
        environment.
        '''
        self.app, self.window = run()

    def tearDown(self):
        '''
        Method run after each test is run. Use this to reset the testing
        environment.
        '''
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

    def test_runButton(self):
        self.window.right_widget.test_mode = True
        QTest.mouseClick(self.window.right_widget.run, Qt.LeftButton)
        self.assertEqual(True, self.window.right_widget.test_click)


if __name__ == '__main__':
    unittest.main()

import sys
import unittest
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from functioning_UI_PyQt import run

class ViewerTester(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()


### NOTES ###
'''
- Initially just test the 'Run' button in bottom rh corner
- This is within app settings (self.run)
'''

import sys
import unittest
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from thread import WorkerThread
from functioning_UI_PyQt import Controller, AppSettings, AppSettingsBrowseMode

class RightWidgetTester(unittest.TestCase):
    ''' Class to perform unit tests on the buttons within the right widget of the
        GUI Launcher.
    '''
    def setUp(self):
        '''Method run before every test. Use this to prepare the test fixture.'''
        self.controller = Controller()
        self.w = self.controller.window1.right_widget
        self.w.testing = True
        Controller.allWidgets_setCheckable(self.controller.app)

    def tearDown(self):
        ''' Method run after each test is run. Use this to reset the testing
            environment.'''
        self.w.close()
        self.controller.app.quit()
        self.controller.app, self.w = None, None

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
        self.assertTrue(self.w.exit.isChecked())

    def test_runButton(self):
        QTest.mouseClick(self.w.run, Qt.LeftButton)
        self.assertTrue(self.w.run.isChecked())

    def test_browseModelsButton(self):
        QTest.mouseClick(self.w.load_edit, Qt.LeftButton)
        self.assertTrue(self.w.load_edit.isChecked())

    def test_browseLandmarksButton(self):
        QTest.mouseClick(self.w.landmark_file_edit, Qt.LeftButton)
        self.assertTrue(self.w.landmark_file_edit.isChecked())

    def test_browseModeButton(self):
        QTest.mouseClick(self.w.browseMode, Qt.LeftButton)
        self.assertTrue(self.w.browseMode.isChecked())

    # def test_browseLogsButton(self):
    #     QTest.mouseClick(self.w.log_dir_edit, Qt.LeftButton)
    #     self.assertTrue(self.w.test_click)

    # def test_GIFCheckBox(self):
    #     QTest.mouseClick(self.w.GIF_edit, Qt.LeftButton)
    #     self.assertTrue(self.w.GIF_edit.isChecked(),
    #         pos=QtCore.QPoint(2,self.w.GIF_edit.height()/2))
    #
    # def test_videoCheckBox(self):
    #     QTest.mouseClick(self.w.video_edit, Qt.LeftButton)
    #     self.assertTrue(self.w.test_click)


class RightWidgetBrowseModeTester(unittest.TestCase):
    ''' Tester for browse mode
    '''
    def setUp(self):
        '''Method run before every test. Use this to prepare the test fixture.'''
        self.controller = Controller()
        self.controller.show_browseMode()
        self.w = self.controller.window2.right_widget
        self.w.testing = True
        Controller.allWidgets_setCheckable(self.controller.app)

    def tearDown(self):
        ''' Method run after each test is run. Use this to reset the testing
            environment.'''
        self.w.close()
        self.controller.app.quit()
        self.controller.app, self.w = None, None

    def test_exitButton(self):
        QTest.mouseClick(self.w.exit, Qt.LeftButton)
        self.assertTrue(self.w.exit.isChecked())

    def test_browseImgsButton(self):
        QTest.mouseClick(self.w.img_file_edit, Qt.LeftButton)
        self.assertTrue(self.w.img_file_edit.isChecked())

    def test_upButton(self):
        QTest.mouseClick(self.w.upButton, Qt.LeftButton)
        self.assertTrue(self.w.upButton.isChecked())

    def test_downButton(self):
        QTest.mouseClick(self.w.downButton, Qt.LeftButton)
        self.assertTrue(self.w.downButton.isChecked())

    def test_leftButton(self):
        QTest.mouseClick(self.w.leftButton, Qt.LeftButton)
        self.assertTrue(self.w.leftButton.isChecked())

    def test_rightButton(self):
        QTest.mouseClick(self.w.rightButton, Qt.LeftButton)
        self.assertTrue(self.w.rightButton.isChecked())

    def test_inButton(self):
        QTest.mouseClick(self.w.inButton, Qt.LeftButton)
        self.assertTrue(self.w.inButton.isChecked())

    def test_outButton(self):
        QTest.mouseClick(self.w.outButton, Qt.LeftButton)
        self.assertTrue(self.w.outButton.isChecked())

    def test_zoomInButton(self):
        QTest.mouseClick(self.w.zoomInButton, Qt.LeftButton)
        self.assertTrue(self.w.zoomInButton.isChecked())

    def test_zoomOutButton(self):
        QTest.mouseClick(self.w.zoomOutButton, Qt.LeftButton)
        self.assertTrue(self.w.zoomOutButton.isChecked())


class LeftWidgetTester(unittest.TestCase):
    '''Same as above but for the left widget'''
    def setUp(self):
        '''Method run before every test. Use this to prepare the test fixture.'''
        self.controller = Controller()
        self.w = self.controller.window1.left_widget
        self.w.testing = True
        Controller.allWidgets_setCheckable(self.controller.app)

    def tearDown(self):
        ''' Method run after each test is run. Use this to reset the testing
            environment.'''
        self.w.close()
        self.controller.app.quit()
        self.controller.app, self.w = None, None

    def test_startButton(self):
        QTest.mouseClick(self.w.run_button, Qt.LeftButton)
        self.assertTrue(self.w.run_button.isChecked())

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


class ControllerTester(unittest.TestCase):
    ''' Tester for browse mode
    '''
    def _setUp_default(self):
        '''Method run before every test. Use this to prepare the test fixture.'''
        self.controller = Controller()
        self.w = self.controller.window1.right_widget
        self.w.testing = True
        Controller.allWidgets_setCheckable(self.controller.app)

    def _setUp_browseMode(self):
        '''Method run before every test. Use this to prepare the test fixture.'''
        self.controller = Controller()
        self.controller.show_browseMode()
        self.w = self.controller.window2.right_widget
        self.w.testing = True
        Controller.allWidgets_setCheckable(self.controller.app)

    def tearDown(self):
        ''' Method run after each test is run. Use this to reset the testing
            environment.'''
        self.w.close()
        self.controller.app.quit()
        self.controller.app, self.w = None, None

    def test_switchBrowseMode(self):
        self._setUp_default()
        QTest.mouseClick(self.w.browseMode, Qt.LeftButton)
        self.assertTrue(isinstance(self.controller.app_settings, AppSettingsBrowseMode))

    def test_switchDefault(self):
        self._setUp_browseMode()
        QTest.mouseClick(self.w.testMode, Qt.LeftButton)
        self.assertTrue(isinstance(self.controller.app_settings, AppSettings))


if __name__ == '__main__':
    unittest.main()

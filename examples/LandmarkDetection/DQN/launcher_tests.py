import sys
import unittest
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from thread import WorkerThread
from controller import Controller, Tab
from right_widget_automatic import RightWidgetSettings
from right_widget_browse import RightWidgetSettingsBrowseMode, XMove, YMove, ZMove
from left_widget import LeftWidgetSettings
import numpy as np
import glob
import os
import pickle

class RightWidgetTester(unittest.TestCase):
    ''' Class to perform unit tests on the buttons and functionatlity within 
        the right widget of the GUI Launcher.
    '''
    def setUp(self):
        '''Method run before every test. Use this to prepare the test fixture.'''
        self.controller = Controller()
        self.m = self.controller.right_widget.automatic_mode
        self.w = self.m.window
        Controller.allWidgets_setCheckable(self.controller.app)
        
    def tearDown(self):
        ''' Method run after each test is run. Use this to reset the testing
            environment.

            Raises ValueError to progress onto next test as unittest doesn't
            work correctly with threading & PyQt.
        '''
        try:
            test_results[self.id()] = self._outcome.errors[1][1][1]
        except TypeError:
            test_results[self.id()] = 'success'

        raise ValueError('Stop test here')

    def test_taskRadioButton(self):
        ''' Check the task button changes between play and eval modes
        '''
        # Check default
        self.assertEqual(self.m.which_task(), 'Play')
        # Change to eval mode and check
        QTest.mouseClick(self.m.eval_button, Qt.LeftButton)
        self.assertEqual(self.m.which_task(), 'Evaluation')
        # Change back to play mode and check
        QTest.mouseClick(self.m.play_button, Qt.LeftButton)
        self.assertEqual(self.m.which_task(), 'Play')

    def test_agentSpeedSlider(self):
        '''Checks if the slider works and if it adjusts the thread speed'''
        # Check initial position is correct
        self.slider_checker()

        # Change to min value
        self.m.speed_slider.setValue(self.m.speed_slider.minimum())
        self.assertEqual(self.m.speed_slider.value(), self.m.speed_slider.minimum())
        self.slider_checker()

        # Change to medium value
        self.m.speed_slider.setValue(round((self.m.speed_slider.maximum() - \
            self.m.speed_slider.minimum()) / 2, 1) )
        self.slider_checker()

    def slider_checker(self):
        ''' Helper function for checking slider position corresponds to correct
            thread speed
        '''
        if self.m.speed_slider.value() == self.m.speed_slider.maximum():
            self.assertEqual(self.m.thread.speed, WorkerThread.FAST)
        elif self.m.speed_slider.value() == self.m.speed_slider.minimum():
            self.assertEqual(self.m.thread.speed, WorkerThread.SLOW)
        else:
            self.assertEqual(self.m.thread.speed, WorkerThread.MEDIUM)

    def test_runTerminateButtons(self):
        ''' Check if the run and terminate begin and end the RL loop as expected '''
        # Check run button
        QTest.mouseClick(self.m.run_button, Qt.LeftButton)
        self.assertTrue(self.m.run_button.isChecked())
        self.assertEqual(self.m.run_button.text(), self.m.PAUSE)

        # Check pause button pauses thread
        QTest.mouseClick(self.m.run_button, Qt.LeftButton)
        self.assertTrue(self.m.thread.pause)
        self.assertEqual(self.m.run_button.text(), self.m.RESUME)

        # Check resume button reverses above
        QTest.mouseClick(self.m.run_button, Qt.LeftButton)
        self.assertTrue(not self.m.thread.pause)
        self.assertEqual(self.m.run_button.text(), self.m.PAUSE)

        # Check terminate button kills thread
        QTest.mouseClick(self.m.terminate_button, Qt.LeftButton)
        self.assertTrue(self.m.thread.terminate)

        # Check logs displayed correctly
        for msg in ['Terminate', 'Start', 'Pause', 'Resume']:
            self.assertTrue(self.m.terminal.toPlainText().find(msg))


class RightWidgetBrowseModeTester(unittest.TestCase):
    ''' Class to perform unit tests on the buttons and functionatlity within 
        the right widget of the GUI Launcher while browse mode is activated.
    '''
    def setUp(self):
        '''Method run before every test. Use this to prepare the test fixture.'''
        self.controller = Controller()
        self.m = self.controller.right_widget.browse_mode
        self.w = self.m.window
        self.controller.right_widget.tab_widget.setCurrentIndex(1)      # Change to browse mode
        Controller.allWidgets_setCheckable(self.controller.app)
        
    def tearDown(self):
        ''' Method run after each test is run. Use this to reset the testing
            environment.

            Raises ValueError to progress onto next test as unittest doesn't
            work correctly with threading & PyQt.
        '''
        try:
            test_results[self.id()] = self._outcome.errors[1][1][1]
        except TypeError:
            test_results[self.id()] = 'success'

        raise ValueError('Stop test here')

    # def test_browseImgsButton(self):
    #     QTest.mouseClick(self.w.img_file_edit, Qt.LeftButton)
    #     self.assertTrue(self.w.img_file_edit.isChecked())

    def test_upButton(self):
        ''' Check clicking the up button moves the agent '''
        init_loc = self.m.env._location
        QTest.mouseClick(self.m.y_action.up_button, Qt.LeftButton)
        self.assertTrue(self.m.y_action.up_button.isChecked())
        self.assertNotEqual(init_loc, self.m.env._location)

    def test_downButton(self):
        ''' Check clicking the down button moves the agent '''
        init_loc = self.m.env._location
        QTest.mouseClick(self.m.y_action.down_button, Qt.LeftButton)
        self.assertTrue(self.m.y_action.down_button.isChecked())
        self.assertNotEqual(init_loc, self.m.env._location)

    def test_leftButton(self):
        ''' Check clicking the left button moves the agent '''
        init_loc = self.m.env._location
        QTest.mouseClick(self.m.x_action.left_button, Qt.LeftButton)
        self.assertTrue(self.m.x_action.left_button.isChecked())
        self.assertNotEqual(init_loc, self.m.env._location)

    def test_rightButton(self):
        ''' Check clicking the left button moves the agent '''
        init_loc = self.m.env._location
        QTest.mouseClick(self.m.x_action.right_button, Qt.LeftButton)
        self.assertTrue(self.m.x_action.right_button.isChecked())
        self.assertNotEqual(init_loc, self.m.env._location)

    def test_zInButton(self):
        ''' Check clicking the z in button moves the agent '''
        init_loc = self.m.env._location
        QTest.mouseClick(self.m.z_action.in_button, Qt.LeftButton)
        self.assertTrue(self.m.z_action.in_button.isChecked())
        self.assertNotEqual(init_loc, self.m.env._location)

    def test_zOutButton(self):
        ''' Check clicking the z out button moves the agent '''
        init_loc = self.m.env._location
        QTest.mouseClick(self.m.z_action.out_button, Qt.LeftButton)
        self.assertTrue(self.m.z_action.out_button.isChecked())
        self.assertNotEqual(init_loc, self.m.env._location)

    def test_zoomInButton(self):
        ''' Check clicking the zoom in button registers '''
        QTest.mouseClick(self.m.zoomInButton, Qt.LeftButton)
        self.assertTrue(self.m.zoomInButton.isChecked())

    def test_zoomOutButton(self):
        ''' Check clicking the zoom in button registers '''
        QTest.mouseClick(self.m.zoomOutButton, Qt.LeftButton)
        self.assertTrue(self.m.zoomOutButton.isChecked())

    def test_nextImgButton(self):
        ''' Check clicking next image loads a new image by comparing 
            the intensity of the initial img to new img
        '''
        init_intensity = np.sum(self.m.env.viewer.widget.arr)
        QTest.mouseClick(self.m.next_img, Qt.LeftButton)
        self.assertTrue(self.m.next_img.isChecked())
        self.assertTrue(init_intensity - np.sum(self.m.env.viewer.widget.arr) > 1e-5)

    def test_delHITLButton_notClickable(self):
        ''' Check the HITL delete button is not clickable if
            HITL mode is not enabled.
        '''
        QTest.mouseClick(self.m.HITL_delete, Qt.LeftButton)
        self.assertTrue(not self.m.HITL_delete.isChecked())


class RightWidgetHITLTester(unittest.TestCase):
    ''' Tester for the functionality of HITL mode within browse mode on right
        widget.
    '''
    def setUp(self):
        '''Method run before every test. Use this to prepare the test fixture.'''
        self.controller = Controller()
        self.m = self.controller.right_widget.browse_mode
        self.w = self.m.window
        self.controller.right_widget.on_change(1)
        Controller.allWidgets_setCheckable(self.controller.app)

        self.m.testing = True
        self.m.HITL = True

    def tearDown(self):
        ''' Method run after each test is run. Use this to reset the testing
            environment.

            Raises ValueError to progress onto next test as unittest doesn't
            work correctly with threading & PyQt.
        '''
        try:
            test_results[self.id()] = self._outcome.errors[1][1][1]
        except (TypeError, IndexError):
            test_results[self.id()] = 'success'

        raise ValueError('Stop test here')

    def test_enableHITLCheckBox(self):
        ''' Test the HITL checkbox works '''
        self.m.HITL = False
        QTest.mouseClick(self.m.HITL_mode, Qt.LeftButton)
        self.assertTrue(self.m.HITL_mode.isChecked())

    def test_delHITLButton(self):
        ''' Test the HITL delete episode deletes the latest episode as expected.
        '''
        # Move to fill location history
        QTest.mouseClick(self.m.y_action.down_button, Qt.LeftButton)
        QTest.mouseClick(self.m.y_action.up_button, Qt.LeftButton)

        # Delete episode
        QTest.mouseClick(self.m.HITL_delete, Qt.LeftButton)
        self.assertEqual(self.m.HITL_logger, [])

    def test_saveHITL(self):
        ''' Test the HITL session is saved when HITL mode is disabled 
        '''
        # Move to fill location history
        QTest.mouseClick(self.m.y_action.down_button, Qt.LeftButton)
        QTest.mouseClick(self.m.y_action.up_button, Qt.LeftButton)

        # End HITL mode (as this calls save_HITL())
        QTest.mouseClick(self.m.HITL_mode, Qt.LeftButton)
        self.assertTrue(not self.m.HITL_mode.isChecked())

        # Load the created file
        list_of_files = glob.glob('./data/HITL/*.pickle')
        latest_file = max(list_of_files, key=os.path.getctime)
        with open(latest_file, 'rb') as f:
            log = pickle.load(f)

        # Check contents of the log are correct
        self.assertEqual(len(log), 1)
        self.assertEqual(len(log[0]['states']), 3)
        self.assertEqual(len(log[0]['rewards']), 3)
        self.assertEqual(len(log[0]['actions']), 3)
        self.assertEqual(log[0]['is_over'][-1], 1)
        self.assertEqual(np.unique(log[0]['is_over'][:-1])[0], 0)
        self.assertTrue(([i in [1,2,3] for i in log[0]['resolution']].count(True)
                        == len(log[0]['resolution'])))
        self.assertTrue((log[0]['img_name'].startswith('ADNI') or
                        log[0]['img_name'].startswith('iFIND') or
                        log[0]['img_name'].startswith('14')))

        # Delete the log file
        os.remove(latest_file)

    def test_checkHITLZoom(self):
        ''' Check that changing resolution doesn't make an action '''
        buttons = [self.m.zoomInButton, self.m.zoomOutButton]
        for button in buttons:
            QTest.mouseClick(button, Qt.LeftButton)
            self.assertEqual(self.m.HITL_logger, [])

    def test_bufferFillsCorrectly(self):
        ''' Check that the buffer fills correctly with the agent's movement.
        '''
        # Move to fill location history
        QTest.mouseClick(self.m.y_action.up_button, Qt.LeftButton)
        QTest.mouseClick(self.m.x_action.left_button, Qt.LeftButton)
        QTest.mouseClick(self.m.z_action.out_button, Qt.LeftButton)

        # End HITL mode (as this calls save_HITL())
        QTest.mouseClick(self.m.HITL_mode, Qt.LeftButton)

        # Load the created file
        list_of_files = glob.glob('./data/HITL/*.pickle')
        latest_file = max(list_of_files, key=os.path.getctime)
        with open(latest_file, 'rb') as f:
            log = pickle.load(f)

        # Check contents of the log are correct
        self.assertEqual(len(log), 1)
        self.assertEqual(len(log[0]['actions']), 4)
        self.assertEqual(log[0]['actions'][1:], [1, 3, 5])

        # Delete the log file
        os.remove(latest_file)


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

    # def test_browseModelsButton(self):
    #     QTest.mouseClick(self.w.load_edit, Qt.LeftButton)
    #     self.assertTrue(self.w.load_edit.isChecked())

    # def test_browseLandmarksButton(self):
    #     QTest.mouseClick(self.w.landmark_file_edit, Qt.LeftButton)
    #     self.assertTrue(self.w.landmark_file_edit.isChecked())

    # def test_browseModeButton(self):
    #     QTest.mouseClick(self.w.browseMode, Qt.LeftButton)
    #     self.assertTrue(self.w.browseMode.isChecked())


class ControllerTester(unittest.TestCase):
    ''' Tester for controller class
    '''
    def setUp(self):
        '''Method run before every test. Use this to prepare the test fixture.'''
        self.controller = Controller()
        self.w = self.controller.right_widget.automatic_mode.window
        Controller.allWidgets_setCheckable(self.controller.app)
        
    def tearDown(self):
        ''' Method run after each test is run. Use this to reset the testing
            environment.

            Raises ValueError to progress onto next test as unittest doesn't
            work correctly with threading & PyQt.
        '''
        try:
            test_results[self.id()] = self._outcome.errors[1][1][1]
        except TypeError:
            test_results[self.id()] = 'success'

        raise ValueError('Stop test here')

    def test_switchModes(self):
        ''' Test to ensure moving between Default Mode and Browse Mode tabs work 
            correctly
        '''
        # Test default mode is showing
        self.assertEqual(self.controller.right_widget.tab_widget.currentIndex(), 0)

        # Change to browse mode and test again
        self.controller.right_widget.tab_widget.setCurrentIndex(1)
        self.assertEqual(self.controller.right_widget.tab_widget.currentIndex(), 1)
        
        # Change back to default mode and test again
        self.controller.right_widget.tab_widget.setCurrentIndex(0)
        self.assertEqual(self.controller.right_widget.tab_widget.currentIndex(), 0)

    def test_load_defaults(self):
        ''' Test to check browse mode loads an image as expected
        '''
        # Change to browse mode
        self.controller.right_widget.tab_widget.setCurrentIndex(1)
        self.assertTrue(abs(np.sum(self.w.widget.arr)) > 1e-5)


if __name__ == '__main__':
    test_results = {}

    classes_to_test = [
        # RightWidgetTester,
        # RightWidgetBrowseModeTester,
        # RightWidgetHITLTester,
        LeftWidgetTester,
        # ControllerTester,
    ]

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in classes_to_test:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(big_suite)

    print(test_results)
    print(f'\nTests passed: {list(test_results.values()).count("success")} / {len(test_results)}\n')
    # unittest.main()

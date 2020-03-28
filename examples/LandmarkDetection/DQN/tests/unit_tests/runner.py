import unittest
from tests.unit_tests import launcher_tests

if __name__ == '__main__':
    # initialize the test suite
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    # add tests to the test suite
    suite.addTests(loader.loadTestsFromModule(launcher_tests))

    # initialize a runner, pass it your suite and run it
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

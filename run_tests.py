import unittest
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import test modules
from tests.test_user_controller import TestUserController
from tests.test_validation import TestValidation
from tests.test_date_utils import TestDateUtils
from tests.test_flight_controller import TestFlightController

# Import new test modules
from tests.test_validation_functions import TestValidationFunctions
from tests.test_date_functions import TestDateFunctions
from tests.test_user_controller_functions import TestUserControllerFunctions
from tests.test_flight_controller_functions import TestFlightControllerFunctions

if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()

    # Add test cases to the suite
    test_suite.addTest(unittest.makeSuite(TestUserController))
    test_suite.addTest(unittest.makeSuite(TestValidation))
    test_suite.addTest(unittest.makeSuite(TestDateUtils))
    test_suite.addTest(unittest.makeSuite(TestFlightController))

    # Add new test cases to the suite
    test_suite.addTest(unittest.makeSuite(TestValidationFunctions))
    test_suite.addTest(unittest.makeSuite(TestDateFunctions))
    test_suite.addTest(unittest.makeSuite(TestUserControllerFunctions))
    test_suite.addTest(unittest.makeSuite(TestFlightControllerFunctions))

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())

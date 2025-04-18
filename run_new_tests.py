import unittest
import sys
import os

# Добавляем корневую директорию проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Импортируем новые тестовые модули
from tests.test_validation_functions import TestValidationFunctions
from tests.test_date_functions import TestDateFunctions
from tests.test_user_controller_functions import TestUserControllerFunctions
from tests.test_flight_controller_functions import TestFlightControllerFunctions

if __name__ == '__main__':
    # Создаем загрузчик тестов
    loader = unittest.TestLoader()

    # Создаем набор тестов
    test_suite = unittest.TestSuite()

    # Добавляем новые тесты в набор
    test_suite.addTests(loader.loadTestsFromTestCase(TestValidationFunctions))
    test_suite.addTests(loader.loadTestsFromTestCase(TestDateFunctions))
    test_suite.addTests(loader.loadTestsFromTestCase(TestUserControllerFunctions))
    test_suite.addTests(loader.loadTestsFromTestCase(TestFlightControllerFunctions))

    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Выходим с ненулевым кодом, если тесты не прошли
    sys.exit(not result.wasSuccessful())

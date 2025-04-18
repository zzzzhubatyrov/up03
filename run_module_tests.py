import unittest
import sys
import os

# Добавляем корневую директорию проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Импортируем модульные тестовые классы
from tests.test_ticket_pricing import TestTicketPricing
from tests.test_schedule_management import TestScheduleManagement
from tests.test_flight_filtering import TestFlightFiltering
from tests.test_route_management import TestRouteManagement

if __name__ == '__main__':
    # Создаем загрузчик тестов
    loader = unittest.TestLoader()

    # Создаем набор тестов
    test_suite = unittest.TestSuite()

    # Добавляем тесты в набор
    test_suite.addTests(loader.loadTestsFromTestCase(TestTicketPricing))
    test_suite.addTests(loader.loadTestsFromTestCase(TestScheduleManagement))
    test_suite.addTests(loader.loadTestsFromTestCase(TestFlightFiltering))
    test_suite.addTests(loader.loadTestsFromTestCase(TestRouteManagement))

    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Выходим с ненулевым кодом, если тесты не прошли
    sys.exit(not result.wasSuccessful())

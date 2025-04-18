import unittest
import sys
import os

# Добавляем корневую директорию проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Импортируем тестовые модули
from tests.test_auth import TestAuthentication
from tests.test_user_management import TestUserManagement
from tests.test_user_session import TestUserSession
from tests.test_login_view import TestLoginView

if __name__ == '__main__':
    # Создаем набор тестов
    test_suite = unittest.TestSuite()
    
    # Добавляем тесты в набор
    test_suite.addTest(unittest.makeSuite(TestAuthentication))
    test_suite.addTest(unittest.makeSuite(TestUserManagement))
    test_suite.addTest(unittest.makeSuite(TestUserSession))
    test_suite.addTest(unittest.makeSuite(TestLoginView))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Выходим с ненулевым кодом, если тесты не прошли
    sys.exit(not result.wasSuccessful())

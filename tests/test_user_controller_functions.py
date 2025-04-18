import unittest
import sys
import os
import datetime

# Добавляем корневую директорию проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.controllers.user_controller import UserController
from app.models import User, Role, Office, Country, UserSession
from app.config.database import get_session

class TestUserControllerFunctions(unittest.TestCase):
    """Тесты для функций контроллера пользователей"""

    def setUp(self):
        """Подготовка перед каждым тестом"""
        self.session = get_session()
        
        # Создаем тестовые данные, если они не существуют
        self._ensure_test_data()

    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаляем тестового пользователя, если он был создан
        test_user = self.session.query(User).filter_by(email="test_user@example.com").first()
        if test_user:
            self.session.delete(test_user)
            self.session.commit()

    def _ensure_test_data(self):
        """Убеждаемся, что необходимые тестовые данные существуют"""
        # Проверяем наличие роли пользователя
        user_role = self.session.query(Role).filter_by(title="user").first()
        if not user_role:
            user_role = Role(title="user")
            self.session.add(user_role)
            self.session.commit()
        
        # Проверяем наличие страны
        country = self.session.query(Country).first()
        if not country:
            country = Country(name="Test Country")
            self.session.add(country)
            self.session.commit()
        
        # Проверяем наличие офиса
        office = self.session.query(Office).first()
        if not office:
            office = Office(
                country_id=country.id,
                title="Test Office",
                phone="+1-555-1234",
                contact="Test Contact"
            )
            self.session.add(office)
            self.session.commit()

    def test_add_user(self):
        """Тест функции добавления пользователя"""
        # Получаем офис для теста
        office = self.session.query(Office).first()
        
        # Тестируем добавление пользователя
        success, message = UserController.add_user(
            email="test_user@example.com",
            firstname="Test",
            lastname="User",
            office_title=office.title,
            password="password123",
            birthdate=datetime.datetime(1990, 1, 1),
            role_title="user"
        )
        
        # Проверяем результат
        self.assertTrue(success)
        self.assertEqual(message, "User added successfully")
        
        # Проверяем, что пользователь действительно добавлен в базу
        user = self.session.query(User).filter_by(email="test_user@example.com").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.firstname, "Test")
        self.assertEqual(user.lastname, "User")
        self.assertEqual(user.password, "password123")
        
        # Тестируем добавление пользователя с существующим email
        success, message = UserController.add_user(
            email="test_user@example.com",
            firstname="Another",
            lastname="User",
            office_title=office.title,
            password="password456",
            birthdate=datetime.datetime(1995, 5, 5),
            role_title="user"
        )
        
        # Проверяем результат
        self.assertFalse(success)
        self.assertEqual(message, "User with this email already exists")

    def test_toggle_active(self):
        """Тест функции включения/отключения учетной записи пользователя"""
        # Получаем офис и роль для теста
        office = self.session.query(Office).first()
        role = self.session.query(Role).filter_by(title="user").first()
        
        # Создаем тестового пользователя
        user = User(
            office_id=office.id,
            role_id=role.id,
            email="test_user@example.com",
            password="password123",
            firstname="Test",
            lastname="User",
            birthdate=datetime.datetime(1990, 1, 1),
            active=True
        )
        self.session.add(user)
        self.session.commit()
        
        # Тестируем отключение учетной записи
        success, message = UserController.toggle_active(user.id)
        
        # Проверяем результат
        self.assertTrue(success)
        self.assertEqual(message, "Учетная запись пользователя отключена")
        
        # Проверяем, что статус пользователя изменился
        user = self.session.query(User).get(user.id)
        self.assertFalse(user.active)
        
        # Тестируем включение учетной записи
        success, message = UserController.toggle_active(user.id)
        
        # Проверяем результат
        self.assertTrue(success)
        self.assertEqual(message, "Учетная запись пользователя включена")
        
        # Проверяем, что статус пользователя изменился
        user = self.session.query(User).get(user.id)
        self.assertTrue(user.active)
        
        # Тестируем с несуществующим ID пользователя
        success, message = UserController.toggle_active(9999)
        
        # Проверяем результат
        self.assertFalse(success)
        self.assertEqual(message, "Пользователь не найден")

    def test_authenticate(self):
        """Тест функции аутентификации пользователя"""
        # Получаем офис и роль для теста
        office = self.session.query(Office).first()
        role = self.session.query(Role).filter_by(title="user").first()
        
        # Создаем тестового пользователя
        user = User(
            office_id=office.id,
            role_id=role.id,
            email="test_user@example.com",
            password="password123",
            firstname="Test",
            lastname="User",
            birthdate=datetime.datetime(1990, 1, 1),
            active=True
        )
        self.session.add(user)
        self.session.commit()
        
        # Тестируем успешную аутентификацию
        result_user, session = UserController.authenticate("test_user@example.com", "password123")
        
        # Проверяем результат
        self.assertIsNotNone(result_user)
        self.assertEqual(result_user.id, user.id)
        self.assertIsNotNone(session)
        self.assertEqual(session.user_id, user.id)
        
        # Тестируем неверный пароль
        result_user, message = UserController.authenticate("test_user@example.com", "wrong_password")
        
        # Проверяем результат
        self.assertIsNone(result_user)
        self.assertEqual(message, "Неверный email или пароль")
        
        # Тестируем несуществующий email
        result_user, message = UserController.authenticate("nonexistent@example.com", "password123")
        
        # Проверяем результат
        self.assertIsNone(result_user)
        self.assertEqual(message, "Неверный email или пароль")
        
        # Тестируем отключенную учетную запись
        user.active = False
        self.session.commit()
        
        result_user, message = UserController.authenticate("test_user@example.com", "password123")
        
        # Проверяем результат
        self.assertIsNone(result_user)
        self.assertEqual(message, "Ваша учетная запись отключена администратором")

    def test_close_session(self):
        """Тест функции закрытия сеанса пользователя"""
        # Получаем офис и роль для теста
        office = self.session.query(Office).first()
        role = self.session.query(Role).filter_by(title="user").first()
        
        # Создаем тестового пользователя
        user = User(
            office_id=office.id,
            role_id=role.id,
            email="test_user@example.com",
            password="password123",
            firstname="Test",
            lastname="User",
            birthdate=datetime.datetime(1990, 1, 1),
            active=True
        )
        self.session.add(user)
        self.session.commit()
        
        # Создаем сеанс пользователя
        user_session = UserSession(
            user_id=user.id,
            login_time=datetime.datetime.now() - datetime.timedelta(hours=1)  # Вход был час назад
        )
        self.session.add(user_session)
        self.session.commit()
        
        # Тестируем закрытие сеанса
        success = UserController.close_session(user_session)
        
        # Проверяем результат
        self.assertTrue(success)
        
        # Проверяем, что время выхода установлено
        self.session.refresh(user_session)
        self.assertIsNotNone(user_session.logout_time)
        
        # Проверяем, что время выхода больше времени входа
        self.assertGreater(user_session.logout_time, user_session.login_time)
        
        # Проверяем, что функция get_time_spent возвращает корректное значение
        time_spent = user_session.get_time_spent()
        self.assertIsNotNone(time_spent)
        self.assertGreaterEqual(time_spent.total_seconds(), 3600)  # Не менее часа


if __name__ == '__main__':
    unittest.main()

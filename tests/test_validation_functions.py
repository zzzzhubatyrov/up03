import unittest
import sys
import os
import datetime

# Добавляем корневую директорию проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.validation import validate_email, validate_password, validate_date_format, validate_iata_code

class TestValidationFunctions(unittest.TestCase):
    """Тесты для функций валидации"""

    def test_validate_email(self):
        """Тест функции валидации email"""
        # Корректные email
        self.assertTrue(validate_email("user@example.com"))
        self.assertTrue(validate_email("user.name@example.co.uk"))
        self.assertTrue(validate_email("user_name@example-domain.com"))
        self.assertTrue(validate_email("user123@example.ru"))
        
        # Некорректные email
        self.assertFalse(validate_email("user@"))
        self.assertFalse(validate_email("user@.com"))
        self.assertFalse(validate_email("@example.com"))
        self.assertFalse(validate_email("user@example"))
        self.assertFalse(validate_email("user example.com"))
        self.assertFalse(validate_email(""))

    def test_validate_password(self):
        """Тест функции валидации пароля"""
        # Корректные пароли (длина >= 6)
        self.assertTrue(validate_password("password"))
        self.assertTrue(validate_password("pass123"))
        self.assertTrue(validate_password("123456"))
        self.assertTrue(validate_password("P@ssw0rd"))
        
        # Некорректные пароли (длина < 6)
        self.assertFalse(validate_password("pass"))
        self.assertFalse(validate_password("12345"))
        self.assertFalse(validate_password(""))
        
        # Тест с другим минимальным значением
        self.assertTrue(validate_password("1234", min_length=4))
        self.assertFalse(validate_password("123", min_length=4))

    def test_validate_date_format(self):
        """Тест функции валидации формата даты"""
        # Корректные даты в формате dd/mm/yyyy
        self.assertTrue(validate_date_format("01/01/2023"))
        self.assertTrue(validate_date_format("31/12/2022"))
        self.assertTrue(validate_date_format("15/06/2000"))
        
        # Некорректные даты
        self.assertFalse(validate_date_format("2023/01/01"))  # Неверный формат
        self.assertFalse(validate_date_format("01-01-2023"))  # Неверный разделитель
        self.assertFalse(validate_date_format("32/01/2023"))  # Несуществующая дата
        self.assertFalse(validate_date_format("01/13/2023"))  # Несуществующий месяц
        self.assertFalse(validate_date_format(""))            # Пустая строка
        
        # Тест с другим форматом
        self.assertTrue(validate_date_format("2023-01-01", format="%Y-%m-%d"))
        self.assertFalse(validate_date_format("01/01/2023", format="%Y-%m-%d"))

    def test_validate_iata_code(self):
        """Тест функции валидации IATA-кода аэропорта"""
        # Корректные IATA-коды (3 заглавные буквы)
        self.assertTrue(validate_iata_code("JFK"))
        self.assertTrue(validate_iata_code("LAX"))
        self.assertTrue(validate_iata_code("SVO"))
        self.assertTrue(validate_iata_code("DME"))
        
        # Некорректные IATA-коды
        self.assertFalse(validate_iata_code("jfk"))  # Строчные буквы
        self.assertFalse(validate_iata_code("JF"))   # Слишком короткий
        self.assertFalse(validate_iata_code("JFKL")) # Слишком длинный
        self.assertFalse(validate_iata_code("J1K"))  # Содержит цифры
        self.assertFalse(validate_iata_code(""))     # Пустая строка


if __name__ == '__main__':
    unittest.main()

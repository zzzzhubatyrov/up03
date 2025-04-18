import unittest
import sys
import os
import datetime

# Добавляем корневую директорию проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.date_utils import parse_date, format_date, format_time, format_duration, get_date_range

class TestDateFunctions(unittest.TestCase):
    """Тесты для функций работы с датами"""

    def test_parse_date(self):
        """Тест функции парсинга даты из строки"""
        # Корректные даты
        self.assertEqual(parse_date("01/01/2023"), datetime.date(2023, 1, 1))
        self.assertEqual(parse_date("31/12/2022"), datetime.date(2022, 12, 31))
        self.assertEqual(parse_date("15/06/2000"), datetime.date(2000, 6, 15))
        
        # Некорректные даты
        self.assertIsNone(parse_date("2023/01/01"))  # Неверный формат
        self.assertIsNone(parse_date("01-01-2023"))  # Неверный разделитель
        self.assertIsNone(parse_date("32/01/2023"))  # Несуществующая дата
        self.assertIsNone(parse_date("01/13/2023"))  # Несуществующий месяц
        self.assertIsNone(parse_date(""))            # Пустая строка
        
        # Тест с другим форматом
        self.assertEqual(parse_date("2023-01-01", format="%Y-%m-%d"), datetime.date(2023, 1, 1))
        self.assertIsNone(parse_date("01/01/2023", format="%Y-%m-%d"))

    def test_format_date(self):
        """Тест функции форматирования даты в строку"""
        # Тест с объектом datetime.date
        date_obj = datetime.date(2023, 1, 1)
        self.assertEqual(format_date(date_obj), "01/01/2023")
        
        # Тест с объектом datetime.datetime
        datetime_obj = datetime.datetime(2023, 1, 1, 12, 30, 45)
        self.assertEqual(format_date(datetime_obj), "01/01/2023")
        
        # Тест с другим форматом
        self.assertEqual(format_date(date_obj, format="%Y-%m-%d"), "2023-01-01")
        
        # Тест с некорректным значением
        self.assertEqual(format_date(None), "")
        self.assertEqual(format_date("not a date"), "")

    def test_format_time(self):
        """Тест функции форматирования времени в строку"""
        # Тест с объектом datetime.time
        time_obj = datetime.time(12, 30, 45)
        self.assertEqual(format_time(time_obj), "12:30")
        
        # Тест с объектом datetime.datetime
        datetime_obj = datetime.datetime(2023, 1, 1, 12, 30, 45)
        self.assertEqual(format_time(datetime_obj), "12:30")
        
        # Тест с другим форматом
        self.assertEqual(format_time(time_obj, format="%H:%M:%S"), "12:30:45")
        
        # Тест с некорректным значением
        self.assertEqual(format_time(None), "")
        self.assertEqual(format_time("not a time"), "")

    def test_format_duration(self):
        """Тест функции форматирования длительности"""
        # Тест с различными значениями секунд
        self.assertEqual(format_duration(0), "00:00:00")
        self.assertEqual(format_duration(30), "00:00:30")
        self.assertEqual(format_duration(90), "00:01:30")
        self.assertEqual(format_duration(3600), "01:00:00")
        self.assertEqual(format_duration(3661), "01:01:01")
        self.assertEqual(format_duration(86400), "24:00:00")  # 1 день
        
        # Тест с дробным значением (должно округляться)
        self.assertEqual(format_duration(90.5), "00:01:30")

    def test_get_date_range(self):
        """Тест функции получения диапазона дат"""
        # Тестовая дата
        test_date = datetime.date(2023, 1, 15)
        
        # Тест без смещения
        start, end = get_date_range(test_date)
        self.assertEqual(start, test_date)
        self.assertEqual(end, test_date)
        
        # Тест с днями до
        start, end = get_date_range(test_date, days_before=3)
        self.assertEqual(start, datetime.date(2023, 1, 12))
        self.assertEqual(end, test_date)
        
        # Тест с днями после
        start, end = get_date_range(test_date, days_after=3)
        self.assertEqual(start, test_date)
        self.assertEqual(end, datetime.date(2023, 1, 18))
        
        # Тест с днями до и после
        start, end = get_date_range(test_date, days_before=3, days_after=3)
        self.assertEqual(start, datetime.date(2023, 1, 12))
        self.assertEqual(end, datetime.date(2023, 1, 18))


if __name__ == '__main__':
    unittest.main()

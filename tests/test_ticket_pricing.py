import unittest
import sys
import os
import datetime

# Добавляем корневую директорию проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import Schedule, CabinType
from app.config.database import get_session

class TestTicketPricing(unittest.TestCase):
    """Тесты для функций расчета цен билетов"""

    def setUp(self):
        """Подготовка перед каждым тестом"""
        self.session = get_session()
        
        # Получаем существующее расписание или создаем новое для тестов
        self.schedule = self.session.query(Schedule).first()
        if not self.schedule:
            # Создаем тестовое расписание с известной ценой
            from app.models import Route, Aircraft
            route = self.session.query(Route).first()
            aircraft = self.session.query(Aircraft).first()
            
            if route and aircraft:
                self.schedule = Schedule(
                    route_id=route.id,
                    aircraft_id=aircraft.id,
                    date=datetime.date.today(),
                    time=datetime.time(12, 0),
                    flight_number="TEST1",
                    economy_price=100.0,
                    confirmed=True
                )
                self.session.add(self.schedule)
                self.session.commit()

    def test_business_price_calculation(self):
        """Тест расчета цены бизнес-класса (на 35% дороже эконом-класса)"""
        # Проверяем, что расписание существует
        self.assertIsNotNone(self.schedule)
        
        # Проверяем расчет цены бизнес-класса
        economy_price = self.schedule.economy_price
        expected_business_price = int(economy_price * 1.35)
        actual_business_price = self.schedule.business_price
        
        self.assertEqual(actual_business_price, expected_business_price)

    def test_first_class_price_calculation(self):
        """Тест расчета цены первого класса (на 30% дороже бизнес-класса)"""
        # Проверяем, что расписание существует
        self.assertIsNotNone(self.schedule)
        
        # Проверяем расчет цены первого класса
        business_price = self.schedule.business_price
        expected_first_class_price = int(business_price * 1.3)
        actual_first_class_price = self.schedule.first_class_price
        
        self.assertEqual(actual_first_class_price, expected_first_class_price)

    def test_get_price_by_cabin_type(self):
        """Тест получения цены по типу кабины"""
        # Проверяем, что расписание существует
        self.assertIsNotNone(self.schedule)
        
        # Проверяем получение цены для разных типов кабин
        self.assertEqual(self.schedule.get_price_by_cabin_type("economy"), self.schedule.economy_price)
        self.assertEqual(self.schedule.get_price_by_cabin_type("business"), self.schedule.business_price)
        self.assertEqual(self.schedule.get_price_by_cabin_type("first class"), self.schedule.first_class_price)
        
        # Проверяем получение цены для неизвестного типа кабины (должен вернуть цену эконом-класса)
        self.assertEqual(self.schedule.get_price_by_cabin_type("unknown"), self.schedule.economy_price)

    def test_price_relationships(self):
        """Тест соотношения цен между разными классами"""
        # Проверяем, что расписание существует
        self.assertIsNotNone(self.schedule)
        
        # Проверяем, что цена бизнес-класса выше цены эконом-класса
        self.assertGreater(self.schedule.business_price, self.schedule.economy_price)
        
        # Проверяем, что цена первого класса выше цены бизнес-класса
        self.assertGreater(self.schedule.first_class_price, self.schedule.business_price)
        
        # Проверяем точное соотношение цен
        self.assertAlmostEqual(
            self.schedule.business_price / self.schedule.economy_price,
            1.35,
            delta=0.01
        )
        
        self.assertAlmostEqual(
            self.schedule.first_class_price / self.schedule.business_price,
            1.3,
            delta=0.01
        )


if __name__ == '__main__':
    unittest.main()

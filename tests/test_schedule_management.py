import unittest
import sys
import os
import datetime

# Добавляем корневую директорию проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.controllers.flight_controller import FlightController
from app.models import Schedule, Route, Airport
from app.config.database import get_session

class TestScheduleManagement(unittest.TestCase):
    """Тесты для функций управления расписанием рейсов"""

    def setUp(self):
        """Подготовка перед каждым тестом"""
        self.session = get_session()
        
        # Получаем существующее расписание или создаем новое для тестов
        self.schedule = self.session.query(Schedule).first()
        if not self.schedule:
            # Создаем тестовое расписание
            from app.models import Aircraft
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

    def test_toggle_flight_status(self):
        """Тест изменения статуса рейса (подтвержден/отменен)"""
        # Проверяем, что расписание существует
        self.assertIsNotNone(self.schedule)
        
        # Запоминаем исходный статус
        initial_status = self.schedule.confirmed
        
        # Изменяем статус
        success, message = FlightController.toggle_flight_status(self.schedule.id)
        
        # Проверяем результат
        self.assertTrue(success)
        expected_status = "отменен" if initial_status else "подтвержден"
        self.assertEqual(message, f"Рейс {self.schedule.flight_number} {expected_status}")
        
        # Проверяем, что статус действительно изменился
        self.session.refresh(self.schedule)
        self.assertEqual(self.schedule.confirmed, not initial_status)
        
        # Возвращаем статус обратно
        success, message = FlightController.toggle_flight_status(self.schedule.id)
        
        # Проверяем результат
        self.assertTrue(success)
        expected_status = "отменен" if not initial_status else "подтвержден"
        self.assertEqual(message, f"Рейс {self.schedule.flight_number} {expected_status}")
        
        # Проверяем, что статус вернулся к исходному
        self.session.refresh(self.schedule)
        self.assertEqual(self.schedule.confirmed, initial_status)

    def test_get_filtered_schedules_by_flight_number(self):
        """Тест получения отфильтрованного списка расписаний по номеру рейса"""
        # Проверяем, что расписание существует
        self.assertIsNotNone(self.schedule)
        
        # Получаем расписания, отфильтрованные по номеру рейса
        schedules = FlightController.get_filtered_schedules(flight_number=self.schedule.flight_number)
        
        # Проверяем, что список не пустой
        self.assertGreater(len(schedules), 0)
        
        # Проверяем, что все найденные расписания имеют указанный номер рейса
        for schedule in schedules:
            self.assertIn(self.schedule.flight_number, schedule.flight_number)

    def test_get_filtered_schedules_by_date(self):
        """Тест получения отфильтрованного списка расписаний по дате"""
        # Проверяем, что расписание существует
        self.assertIsNotNone(self.schedule)
        
        # Получаем расписания, отфильтрованные по дате
        schedules = FlightController.get_filtered_schedules(date=self.schedule.date)
        
        # Проверяем, что список не пустой
        self.assertGreater(len(schedules), 0)
        
        # Проверяем, что все найденные расписания имеют указанную дату
        for schedule in schedules:
            self.assertEqual(schedule.date, self.schedule.date)

    def test_get_filtered_schedules_by_airports(self):
        """Тест получения отфильтрованного списка расписаний по аэропортам"""
        # Проверяем, что расписание существует
        self.assertIsNotNone(self.schedule)
        
        # Получаем маршрут и аэропорты
        route = self.session.query(Route).get(self.schedule.route_id)
        from_airport = self.session.query(Airport).get(route.departure_airport_id)
        to_airport = self.session.query(Airport).get(route.arrival_airport_id)
        
        # Получаем расписания, отфильтрованные по аэропортам
        schedules = FlightController.get_filtered_schedules(from_airport=from_airport, to_airport=to_airport)
        
        # Проверяем, что список не пустой
        self.assertGreater(len(schedules), 0)
        
        # Проверяем, что все найденные расписания имеют указанные аэропорты
        for schedule in schedules:
            self.assertEqual(schedule.route.departure_airport_id, from_airport.id)
            self.assertEqual(schedule.route.arrival_airport_id, to_airport.id)


if __name__ == '__main__':
    unittest.main()

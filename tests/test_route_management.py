import unittest
import sys
import os
import datetime

# Добавляем корневую директорию проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import Route, Airport, Country
from app.config.database import get_session

class TestRouteManagement(unittest.TestCase):
    """Тесты для функций работы с маршрутами"""

    def setUp(self):
        """Подготовка перед каждым тестом"""
        self.session = get_session()
        
        # Получаем или создаем страну для тестов
        self.country = self.session.query(Country).first()
        if not self.country:
            self.country = Country(name="Test Country")
            self.session.add(self.country)
            self.session.commit()
        
        # Получаем или создаем аэропорты для тестов
        self.airports = []
        for i in range(3):
            airport = self.session.query(Airport).filter_by(iata_code=f"RT{i+1}").first()
            if not airport:
                airport = Airport(
                    country_id=self.country.id,
                    iata_code=f"RT{i+1}",
                    name=f"Route Test Airport {i+1}"
                )
                self.session.add(airport)
            self.airports.append(airport)
        
        self.session.commit()
        
        # Удаляем тестовые маршруты, если они существуют
        for i in range(2):
            route = self.session.query(Route).filter(
                Route.departure_airport_id == self.airports[i].id,
                Route.arrival_airport_id == self.airports[i+1].id
            ).first()
            
            if route:
                self.session.delete(route)
        
        self.session.commit()

    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаляем тестовые маршруты
        for i in range(2):
            route = self.session.query(Route).filter(
                Route.departure_airport_id == self.airports[i].id,
                Route.arrival_airport_id == self.airports[i+1].id
            ).first()
            
            if route:
                self.session.delete(route)
        
        self.session.commit()

    def test_create_route(self):
        """Тест создания маршрута"""
        # Создаем новый маршрут
        route = Route(
            departure_airport_id=self.airports[0].id,
            arrival_airport_id=self.airports[1].id,
            distance=1000,
            flight_time=120
        )
        self.session.add(route)
        self.session.commit()
        
        # Проверяем, что маршрут создан и имеет ID
        self.assertIsNotNone(route.id)
        
        # Проверяем, что маршрут можно найти в базе
        saved_route = self.session.query(Route).get(route.id)
        self.assertIsNotNone(saved_route)
        
        # Проверяем атрибуты маршрута
        self.assertEqual(saved_route.departure_airport_id, self.airports[0].id)
        self.assertEqual(saved_route.arrival_airport_id, self.airports[1].id)
        self.assertEqual(saved_route.distance, 1000)
        self.assertEqual(saved_route.flight_time, 120)

    def test_route_relationships(self):
        """Тест связей маршрута с аэропортами"""
        # Создаем новый маршрут
        route = Route(
            departure_airport_id=self.airports[0].id,
            arrival_airport_id=self.airports[1].id,
            distance=1000,
            flight_time=120
        )
        self.session.add(route)
        self.session.commit()
        
        # Проверяем связь с аэропортом отправления
        self.assertEqual(route.departure_airport.id, self.airports[0].id)
        self.assertEqual(route.departure_airport.iata_code, self.airports[0].iata_code)
        self.assertEqual(route.departure_airport.name, self.airports[0].name)
        
        # Проверяем связь с аэропортом прибытия
        self.assertEqual(route.arrival_airport.id, self.airports[1].id)
        self.assertEqual(route.arrival_airport.iata_code, self.airports[1].iata_code)
        self.assertEqual(route.arrival_airport.name, self.airports[1].name)
        
        # Проверяем обратную связь: маршрут должен быть в списке маршрутов аэропорта отправления
        self.assertIn(route, self.airports[0].departure_routes)
        
        # Проверяем обратную связь: маршрут должен быть в списке маршрутов аэропорта прибытия
        self.assertIn(route, self.airports[1].arrival_routes)

    def test_multiple_routes(self):
        """Тест создания нескольких маршрутов"""
        # Создаем два маршрута
        route1 = Route(
            departure_airport_id=self.airports[0].id,
            arrival_airport_id=self.airports[1].id,
            distance=1000,
            flight_time=120
        )
        
        route2 = Route(
            departure_airport_id=self.airports[1].id,
            arrival_airport_id=self.airports[2].id,
            distance=1500,
            flight_time=180
        )
        
        self.session.add_all([route1, route2])
        self.session.commit()
        
        # Проверяем, что оба маршрута созданы и имеют ID
        self.assertIsNotNone(route1.id)
        self.assertIsNotNone(route2.id)
        
        # Проверяем, что маршруты можно найти в базе
        saved_route1 = self.session.query(Route).get(route1.id)
        saved_route2 = self.session.query(Route).get(route2.id)
        
        self.assertIsNotNone(saved_route1)
        self.assertIsNotNone(saved_route2)
        
        # Проверяем, что у аэропорта в середине есть и входящие, и исходящие маршруты
        middle_airport = self.airports[1]
        
        # Получаем все маршруты для среднего аэропорта
        departure_routes = self.session.query(Route).filter_by(departure_airport_id=middle_airport.id).all()
        arrival_routes = self.session.query(Route).filter_by(arrival_airport_id=middle_airport.id).all()
        
        # Проверяем, что есть хотя бы один исходящий маршрут
        self.assertGreaterEqual(len(departure_routes), 1)
        
        # Проверяем, что есть хотя бы один входящий маршрут
        self.assertGreaterEqual(len(arrival_routes), 1)
        
        # Проверяем, что route1 - это входящий маршрут для среднего аэропорта
        self.assertIn(route1, arrival_routes)
        
        # Проверяем, что route2 - это исходящий маршрут для среднего аэропорта
        self.assertIn(route2, departure_routes)

    def test_route_uniqueness(self):
        """Тест уникальности маршрутов между аэропортами"""
        # Создаем первый маршрут
        route1 = Route(
            departure_airport_id=self.airports[0].id,
            arrival_airport_id=self.airports[1].id,
            distance=1000,
            flight_time=120
        )
        self.session.add(route1)
        self.session.commit()
        
        # Создаем второй маршрут с теми же аэропортами, но другими параметрами
        route2 = Route(
            departure_airport_id=self.airports[0].id,
            arrival_airport_id=self.airports[1].id,
            distance=1100,  # Другое расстояние
            flight_time=130  # Другое время полета
        )
        self.session.add(route2)
        
        # Проверяем, что можно создать второй маршрут между теми же аэропортами
        # (в данной модели нет ограничения уникальности на пару аэропортов)
        try:
            self.session.commit()
            
            # Проверяем, что оба маршрута созданы и имеют ID
            self.assertIsNotNone(route1.id)
            self.assertIsNotNone(route2.id)
            
            # Проверяем, что маршруты можно найти в базе
            saved_route1 = self.session.query(Route).get(route1.id)
            saved_route2 = self.session.query(Route).get(route2.id)
            
            self.assertIsNotNone(saved_route1)
            self.assertIsNotNone(saved_route2)
            
            # Проверяем, что это разные маршруты
            self.assertNotEqual(saved_route1.id, saved_route2.id)
            
            # Проверяем, что у них разные параметры
            self.assertEqual(saved_route1.distance, 1000)
            self.assertEqual(saved_route1.flight_time, 120)
            self.assertEqual(saved_route2.distance, 1100)
            self.assertEqual(saved_route2.flight_time, 130)
            
        except Exception as e:
            # Если возникла ошибка (например, из-за ограничения уникальности),
            # то тест не пройден
            self.fail(f"Не удалось создать второй маршрут между теми же аэропортами: {str(e)}")


if __name__ == '__main__':
    unittest.main()

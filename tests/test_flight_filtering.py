import unittest
import sys
import os
import datetime

# Добавляем корневую директорию проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.controllers.flight_controller import FlightController
from app.models import Schedule, Route, Airport, Aircraft
from app.config.database import get_session

class TestFlightFiltering(unittest.TestCase):
    """Тесты для функций фильтрации рейсов"""

    def setUp(self):
        """Подготовка перед каждым тестом"""
        self.session = get_session()

        # Получаем аэропорты для тестов
        self.airports = self.session.query(Airport).limit(2).all()
        if len(self.airports) < 2:
            # Если недостаточно аэропортов, создаем их
            from app.models import Country
            country = self.session.query(Country).first()
            if country:
                for i in range(2 - len(self.airports)):
                    airport = Airport(
                        country_id=country.id,
                        iata_code=f"TS{i+1}",
                        name=f"Test Airport {i+1}"
                    )
                    self.session.add(airport)
                self.session.commit()
                self.airports = self.session.query(Airport).limit(2).all()

        # Получаем или создаем маршрут между аэропортами
        if len(self.airports) >= 2:
            self.route = self.session.query(Route).filter(
                Route.departure_airport_id == self.airports[0].id,
                Route.arrival_airport_id == self.airports[1].id
            ).first()

            if not self.route:
                self.route = Route(
                    departure_airport_id=self.airports[0].id,
                    arrival_airport_id=self.airports[1].id,
                    distance=1000,
                    flight_time=120
                )
                self.session.add(self.route)
                self.session.commit()

            # Получаем или создаем самолет
            self.aircraft = self.session.query(Aircraft).first()
            if not self.aircraft:
                self.aircraft = Aircraft(
                    name="Test Aircraft",
                    make_model="Test Model",
                    total_seats=180,
                    economy_seats=150,
                    business_seats=30
                )
                self.session.add(self.aircraft)
                self.session.commit()

            # Создаем тестовые расписания на разные даты
            today = datetime.date.today()
            tomorrow = today + datetime.timedelta(days=1)

            # Проверяем, существуют ли уже расписания на эти даты
            self.schedule_today = self.session.query(Schedule).filter(
                Schedule.route_id == self.route.id,
                Schedule.date == today
            ).first()

            if not self.schedule_today:
                self.schedule_today = Schedule(
                    route_id=self.route.id,
                    aircraft_id=self.aircraft.id,
                    date=today,
                    time=datetime.time(12, 0),
                    flight_number="TS100",
                    economy_price=100.0,
                    confirmed=True
                )
                self.session.add(self.schedule_today)

            self.schedule_tomorrow = self.session.query(Schedule).filter(
                Schedule.route_id == self.route.id,
                Schedule.date == tomorrow
            ).first()

            if not self.schedule_tomorrow:
                self.schedule_tomorrow = Schedule(
                    route_id=self.route.id,
                    aircraft_id=self.aircraft.id,
                    date=tomorrow,
                    time=datetime.time(14, 0),
                    flight_number="TS101",
                    economy_price=120.0,
                    confirmed=True
                )
                self.session.add(self.schedule_tomorrow)

            self.session.commit()

    def test_search_flights_direct(self):
        """Тест поиска прямых рейсов"""
        # Проверяем, что у нас есть необходимые данные
        self.assertGreaterEqual(len(self.airports), 2)
        self.assertIsNotNone(self.route)
        self.assertIsNotNone(self.schedule_today)

        # Ищем рейсы на сегодня
        flights_result = FlightController.search_flights(
            self.airports[0].iata_code,
            self.airports[1].iata_code,
            datetime.date.today()
        )

        # Проверяем, что результат является словарем с ключами 'direct' и 'connecting'
        self.assertIsInstance(flights_result, dict)
        self.assertIn('direct', flights_result)
        self.assertIn('connecting', flights_result)

        # Получаем прямые рейсы
        direct_flights = flights_result['direct']

        # Проверяем, что список прямых рейсов не пустой
        self.assertGreater(len(direct_flights), 0)

        # Проверяем, что найденный рейс соответствует нашим критериям
        flight = direct_flights[0]
        self.assertEqual(flight.route.departure_airport_id, self.airports[0].id)
        self.assertEqual(flight.route.arrival_airport_id, self.airports[1].id)
        self.assertEqual(flight.date, datetime.date.today())

    def test_search_flights_extended(self):
        """Тест расширенного поиска рейсов (±3 дня)"""
        # Проверяем, что у нас есть необходимые данные
        self.assertGreaterEqual(len(self.airports), 2)
        self.assertIsNotNone(self.route)
        self.assertIsNotNone(self.schedule_today)
        self.assertIsNotNone(self.schedule_tomorrow)

        # Ищем рейсы на послезавтра с расширенным поиском
        day_after_tomorrow = datetime.date.today() + datetime.timedelta(days=2)
        flights_result = FlightController.search_flights(
            self.airports[0].iata_code,
            self.airports[1].iata_code,
            day_after_tomorrow,
            extended_search=True
        )

        # Проверяем, что результат является словарем с ключами 'direct' и 'connecting'
        self.assertIsInstance(flights_result, dict)
        self.assertIn('direct', flights_result)
        self.assertIn('connecting', flights_result)

        # Получаем прямые рейсы
        direct_flights = flights_result['direct']

        # Проверяем, что список прямых рейсов не пустой (должен найти рейсы на сегодня и завтра)
        self.assertGreater(len(direct_flights), 0)

        # Проверяем, что найдены рейсы в пределах ±3 дней от указанной даты
        for flight in direct_flights:
            date_diff = abs((flight.date - day_after_tomorrow).days)
            self.assertLessEqual(date_diff, 3)

    def test_search_flights_nonexistent(self):
        """Тест поиска несуществующих рейсов"""
        # Проверяем, что у нас есть необходимые данные
        self.assertGreaterEqual(len(self.airports), 2)

        # Ищем рейсы на дату, на которую их точно нет
        far_future_date = datetime.date.today() + datetime.timedelta(days=365)
        flights_result = FlightController.search_flights(
            self.airports[0].iata_code,
            self.airports[1].iata_code,
            far_future_date
        )

        # Проверяем, что результат является словарем с ключами 'direct' и 'connecting'
        self.assertIsInstance(flights_result, dict)
        self.assertIn('direct', flights_result)
        self.assertIn('connecting', flights_result)

        # Проверяем, что список прямых рейсов пустой
        self.assertEqual(len(flights_result['direct']), 0)

        # Проверяем, что список стыковочных рейсов пустой
        self.assertEqual(len(flights_result['connecting']), 0)

    def test_search_flights_invalid_airports(self):
        """Тест поиска рейсов с несуществующими аэропортами"""
        # Ищем рейсы с несуществующим аэропортом отправления
        flights_result = FlightController.search_flights(
            "XXX",  # Несуществующий код
            self.airports[1].iata_code,
            datetime.date.today()
        )

        # Проверяем, что возвращается пустой список
        self.assertEqual(flights_result, [])

        # Ищем рейсы с несуществующим аэропортом прибытия
        flights_result = FlightController.search_flights(
            self.airports[0].iata_code,
            "XXX",  # Несуществующий код
            datetime.date.today()
        )

        # Проверяем, что возвращается пустой список
        self.assertEqual(flights_result, [])


if __name__ == '__main__':
    unittest.main()

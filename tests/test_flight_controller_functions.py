import unittest
import sys
import os
import datetime

# Добавляем корневую директорию проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.controllers.flight_controller import FlightController
from app.models import Airport, Country, Route, Aircraft, Schedule, CabinType, Ticket, User, Role, Office
from app.config.database import get_session

class TestFlightControllerFunctions(unittest.TestCase):
    """Тесты для функций контроллера рейсов"""

    def setUp(self):
        """Подготовка перед каждым тестом"""
        self.session = get_session()
        
        # Создаем тестовые данные, если они не существуют
        self._ensure_test_data()

    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаляем тестовые билеты, если они были созданы
        test_tickets = self.session.query(Ticket).filter_by(booking_reference="TESTBK").all()
        for ticket in test_tickets:
            self.session.delete(ticket)
        
        self.session.commit()

    def _ensure_test_data(self):
        """Убеждаемся, что необходимые тестовые данные существуют"""
        # Проверяем наличие стран
        country = self.session.query(Country).first()
        if not country:
            country = Country(name="Test Country")
            self.session.add(country)
            self.session.commit()
        
        # Проверяем наличие аэропортов
        airport1 = self.session.query(Airport).filter_by(iata_code="TST").first()
        if not airport1:
            airport1 = Airport(
                country_id=country.id,
                iata_code="TST",
                name="Test Airport"
            )
            self.session.add(airport1)
            self.session.commit()
        
        airport2 = self.session.query(Airport).filter_by(iata_code="TST2").first()
        if not airport2:
            airport2 = Airport(
                country_id=country.id,
                iata_code="TST2",
                name="Test Airport 2"
            )
            self.session.add(airport2)
            self.session.commit()
        
        # Проверяем наличие маршрута
        route = self.session.query(Route).filter(
            Route.departure_airport_id == airport1.id,
            Route.arrival_airport_id == airport2.id
        ).first()
        
        if not route:
            route = Route(
                departure_airport_id=airport1.id,
                arrival_airport_id=airport2.id,
                distance=1000,
                flight_time=120
            )
            self.session.add(route)
            self.session.commit()
        
        # Проверяем наличие самолета
        aircraft = self.session.query(Aircraft).first()
        if not aircraft:
            aircraft = Aircraft(
                name="Test Aircraft",
                make_model="Test Model",
                total_seats=180,
                economy_seats=150,
                business_seats=30
            )
            self.session.add(aircraft)
            self.session.commit()
        
        # Проверяем наличие расписания
        schedule = self.session.query(Schedule).filter(
            Schedule.route_id == route.id,
            Schedule.date == datetime.date.today()
        ).first()
        
        if not schedule:
            schedule = Schedule(
                route_id=route.id,
                aircraft_id=aircraft.id,
                date=datetime.date.today(),
                time=datetime.time(12, 0),
                flight_number="TS123",
                economy_price=100.0,
                confirmed=True
            )
            self.session.add(schedule)
            self.session.commit()
        
        # Проверяем наличие типов кабин
        cabin_types = self.session.query(CabinType).all()
        if not cabin_types:
            cabin_types = [
                CabinType(name="Economy"),
                CabinType(name="Business"),
                CabinType(name="First Class")
            ]
            self.session.add_all(cabin_types)
            self.session.commit()
        
        # Проверяем наличие пользователя для тестов
        user_role = self.session.query(Role).filter_by(title="user").first()
        if not user_role:
            user_role = Role(title="user")
            self.session.add(user_role)
            self.session.commit()
        
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
        
        test_user = self.session.query(User).filter_by(email="test_user@example.com").first()
        if not test_user:
            test_user = User(
                office_id=office.id,
                role_id=user_role.id,
                email="test_user@example.com",
                password="password123",
                firstname="Test",
                lastname="User",
                birthdate=datetime.datetime(1990, 1, 1),
                active=True
            )
            self.session.add(test_user)
            self.session.commit()

    def test_get_all_airports(self):
        """Тест функции получения всех аэропортов"""
        # Получаем все аэропорты
        airports = FlightController.get_all_airports()
        
        # Проверяем, что список не пустой
        self.assertGreater(len(airports), 0)
        
        # Проверяем, что все элементы списка являются объектами Airport
        for airport in airports:
            self.assertIsInstance(airport, Airport)
        
        # Проверяем, что наш тестовый аэропорт есть в списке
        test_airport = next((a for a in airports if a.iata_code == "TST"), None)
        self.assertIsNotNone(test_airport)
        self.assertEqual(test_airport.name, "Test Airport")

    def test_search_flights(self):
        """Тест функции поиска рейсов"""
        # Получаем тестовые аэропорты
        airport1 = self.session.query(Airport).filter_by(iata_code="TST").first()
        airport2 = self.session.query(Airport).filter_by(iata_code="TST2").first()
        
        # Ищем рейсы на сегодня
        flights = FlightController.search_flights("TST", "TST2", datetime.date.today())
        
        # Проверяем, что список не пустой
        self.assertGreater(len(flights), 0)
        
        # Проверяем, что найденный рейс соответствует нашим критериям
        flight = flights[0]
        self.assertEqual(flight.route.departure_airport_id, airport1.id)
        self.assertEqual(flight.route.arrival_airport_id, airport2.id)
        self.assertEqual(flight.date, datetime.date.today())
        
        # Ищем рейсы на завтра (не должны найти)
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        flights = FlightController.search_flights("TST", "TST2", tomorrow)
        
        # Проверяем, что список пустой
        self.assertEqual(len(flights), 0)
        
        # Ищем рейсы с расширенным поиском (±3 дня)
        flights = FlightController.search_flights("TST", "TST2", tomorrow, extended_search=True)
        
        # Проверяем, что список не пустой (должен найти рейсы на сегодня)
        self.assertGreater(len(flights), 0)

    def test_toggle_flight_status(self):
        """Тест функции изменения статуса рейса"""
        # Получаем тестовое расписание
        schedule = self.session.query(Schedule).filter_by(flight_number="TS123").first()
        initial_status = schedule.confirmed
        
        # Изменяем статус
        success, message = FlightController.toggle_flight_status(schedule.id)
        
        # Проверяем результат
        self.assertTrue(success)
        expected_status = "отменен" if initial_status else "подтвержден"
        self.assertEqual(message, f"Рейс {schedule.flight_number} {expected_status}")
        
        # Проверяем, что статус действительно изменился
        self.session.refresh(schedule)
        self.assertEqual(schedule.confirmed, not initial_status)
        
        # Возвращаем статус обратно
        success, message = FlightController.toggle_flight_status(schedule.id)
        
        # Проверяем результат
        self.assertTrue(success)
        expected_status = "отменен" if not initial_status else "подтвержден"
        self.assertEqual(message, f"Рейс {schedule.flight_number} {expected_status}")
        
        # Проверяем, что статус вернулся к исходному
        self.session.refresh(schedule)
        self.assertEqual(schedule.confirmed, initial_status)
        
        # Тестируем с несуществующим ID расписания
        success, message = FlightController.toggle_flight_status(9999)
        
        # Проверяем результат
        self.assertFalse(success)
        self.assertEqual(message, "Расписание не найдено")

    def test_book_flight(self):
        """Тест функции бронирования билетов на рейс"""
        # Получаем тестовое расписание и пользователя
        schedule = self.session.query(Schedule).filter_by(flight_number="TS123").first()
        user = self.session.query(User).filter_by(email="test_user@example.com").first()
        
        # Данные пассажиров
        passengers_data = [
            {
                "firstname": "John",
                "lastname": "Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-6789",
                "passport_number": "AB123456",
                "passport_country_id": self.session.query(Country).first().id
            },
            {
                "firstname": "Jane",
                "lastname": "Smith",
                "email": "jane.smith@example.com",
                "phone": "+1-555-9876",
                "passport_number": "CD789012",
                "passport_country_id": self.session.query(Country).first().id
            }
        ]
        
        # Бронируем билеты
        success, message = FlightController.book_flight(
            flight_id=schedule.id,
            cabin_type="Economy",
            passengers_data=passengers_data,
            user_id=user.id
        )
        
        # Проверяем результат
        self.assertTrue(success)
        self.assertIn("Бронирование успешно создано", message)
        
        # Извлекаем номер бронирования из сообщения
        booking_reference = message.split(": ")[1]
        
        # Проверяем, что билеты действительно созданы
        tickets = self.session.query(Ticket).filter_by(booking_reference=booking_reference).all()
        self.assertEqual(len(tickets), 2)
        
        # Проверяем данные билетов
        for i, ticket in enumerate(tickets):
            self.assertEqual(ticket.schedule_id, schedule.id)
            self.assertEqual(ticket.user_id, user.id)
            self.assertEqual(ticket.firstname, passengers_data[i]["firstname"])
            self.assertEqual(ticket.lastname, passengers_data[i]["lastname"])
            self.assertEqual(ticket.email, passengers_data[i]["email"])
            self.assertEqual(ticket.phone, passengers_data[i]["phone"])
            self.assertEqual(ticket.passport_number, passengers_data[i]["passport_number"])
            self.assertEqual(ticket.passport_country_id, passengers_data[i]["passport_country_id"])
            self.assertTrue(ticket.confirmed)


if __name__ == '__main__':
    unittest.main()

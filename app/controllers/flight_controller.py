import datetime
import random
import string
import csv
import io
from app.models import Schedule, Route, Airport, Aircraft, CabinType, Ticket, Country
from app.config.database import get_session
from sqlalchemy import and_, or_

class FlightController:
    """Контроллер для работы с рейсами и билетами"""

    @staticmethod
    def get_all_airports():
        """Получение списка всех аэропортов"""
        session = get_session()
        return session.query(Airport).all()

    @staticmethod
    def get_all_cabin_types():
        """Получение списка всех типов кабин"""
        session = get_session()
        return session.query(CabinType).all()

    @staticmethod
    def get_all_countries():
        """Получение списка всех стран"""
        session = get_session()
        return session.query(Country).all()

    @staticmethod
    def search_flights(from_airport_code, to_airport_code, date, extended_search=False):
        """Поиск рейсов по параметрам"""
        session = get_session()

        # Получаем аэропорты
        from_airport = session.query(Airport).filter_by(iata_code=from_airport_code).first()
        to_airport = session.query(Airport).filter_by(iata_code=to_airport_code).first()

        if not from_airport or not to_airport:
            return []

        # Определяем диапазон дат
        if extended_search:
            start_date = date - datetime.timedelta(days=3)
            end_date = date + datetime.timedelta(days=3)
        else:
            start_date = date
            end_date = date

        # Ищем прямые рейсы
        direct_flights = session.query(Schedule).join(Route).filter(
            Route.departure_airport_id == from_airport.id,
            Route.arrival_airport_id == to_airport.id,
            Schedule.date >= start_date,
            Schedule.date <= end_date,
            Schedule.confirmed == True
        ).all()

        # Ищем рейсы с пересадкой (упрощенный алгоритм)
        connecting_flights = []

        # Получаем все рейсы из аэропорта отправления
        first_leg_flights = session.query(Schedule).join(Route).filter(
            Route.departure_airport_id == from_airport.id,
            Schedule.date >= start_date,
            Schedule.date <= end_date,
            Schedule.confirmed == True
        ).all()

        # Для каждого первого сегмента ищем стыковочный рейс
        for first_leg in first_leg_flights:
            # Получаем аэропорт прибытия первого сегмента
            first_leg_arrival_airport_id = first_leg.route.arrival_airport_id

            # Пропускаем, если это уже пункт назначения
            if first_leg_arrival_airport_id == to_airport.id:
                continue

            # Ищем рейсы из этого аэропорта в пункт назначения
            second_leg_flights = session.query(Schedule).join(Route).filter(
                Route.departure_airport_id == first_leg_arrival_airport_id,
                Route.arrival_airport_id == to_airport.id,
                Schedule.date == first_leg.date,  # Стыковка в тот же день для простоты
                Schedule.time > first_leg.time,   # Время вылета после прибытия первого сегмента
                Schedule.confirmed == True
            ).all()

            # Добавляем стыковочные рейсы в список
            for second_leg in second_leg_flights:
                connecting_flights.append((first_leg, second_leg))

        return {
            'direct': direct_flights,
            'connecting': connecting_flights
        }

    @staticmethod
    def get_flight_by_id(flight_id):
        """Получение рейса по ID"""
        session = get_session()
        return session.query(Schedule).get(flight_id)

    @staticmethod
    def check_seat_availability(flight_id, cabin_type, passengers_count):
        """Проверка наличия свободных мест"""
        session = get_session()
        schedule = session.query(Schedule).get(flight_id)

        if not schedule:
            return False

        # Получаем тип кабины
        cabin_type_obj = session.query(CabinType).filter_by(name=cabin_type).first()
        if not cabin_type_obj:
            return False

        # Считаем существующие билеты
        existing_tickets = session.query(Ticket).filter(
            Ticket.schedule_id == flight_id,
            Ticket.cabin_type_id == cabin_type_obj.id
        ).count()

        # Проверяем, достаточно ли мест
        if cabin_type == "Economy":
            return existing_tickets + passengers_count <= schedule.aircraft.economy_seats
        elif cabin_type == "Business":
            return existing_tickets + passengers_count <= schedule.aircraft.business_seats
        else:  # First Class
            # Предполагаем, что места первого класса = общее - эконом - бизнес
            first_class_seats = schedule.aircraft.total_seats - schedule.aircraft.economy_seats - schedule.aircraft.business_seats
            return existing_tickets + passengers_count <= first_class_seats

    @staticmethod
    def book_flight(flight_id, cabin_type, passengers_data, user_id=None):
        """Бронирование билетов на рейс"""
        session = get_session()

        # Получаем рейс
        schedule = session.query(Schedule).get(flight_id)
        if not schedule:
            return False, "Рейс не найден"

        # Получаем тип кабины
        cabin_type_obj = session.query(CabinType).filter_by(name=cabin_type).first()
        if not cabin_type_obj:
            return False, "Тип кабины не найден"

        # Проверяем наличие мест
        if not FlightController.check_seat_availability(flight_id, cabin_type, len(passengers_data)):
            return False, "Недостаточно свободных мест"

        # Генерируем номер бронирования
        booking_reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        try:
            # Создаем билеты для каждого пассажира
            for passenger in passengers_data:
                ticket = Ticket(
                    user_id=user_id,
                    schedule_id=flight_id,
                    cabin_type_id=cabin_type_obj.id,
                    firstname=passenger['firstname'],
                    lastname=passenger['lastname'],
                    email=passenger.get('email'),
                    phone=passenger.get('phone'),
                    passport_number=passenger['passport_number'],
                    passport_country_id=passenger['passport_country_id'],
                    booking_reference=booking_reference,
                    confirmed=True
                )
                session.add(ticket)

            session.commit()
            return True, f"Бронирование успешно создано. Номер бронирования: {booking_reference}"
        except Exception as e:
            session.rollback()
            return False, f"Ошибка при создании бронирования: {str(e)}"

    @staticmethod
    def update_schedule(schedule_id, date, time, economy_price):
        """Обновление расписания рейса"""
        session = get_session()
        schedule = session.query(Schedule).get(schedule_id)

        if not schedule:
            return False, "Расписание не найдено"

        try:
            schedule.date = date
            schedule.time = time
            schedule.economy_price = economy_price

            session.commit()
            return True, "Расписание успешно обновлено"
        except Exception as e:
            session.rollback()
            return False, f"Ошибка при обновлении расписания: {str(e)}"

    @staticmethod
    def toggle_flight_status(schedule_id):
        """Изменение статуса рейса (подтвержден/отменен)"""
        session = get_session()
        schedule = session.query(Schedule).get(schedule_id)

        if not schedule:
            return False, "Расписание не найдено"

        try:
            schedule.confirmed = not schedule.confirmed

            session.commit()
            status = "подтвержден" if schedule.confirmed else "отменен"
            return True, f"Рейс {schedule.flight_number} {status}"
        except Exception as e:
            session.rollback()
            return False, f"Ошибка при изменении статуса: {str(e)}"

    @staticmethod
    def get_filtered_schedules(from_airport=None, to_airport=None, date=None, flight_number=None, sort_by="date_time"):
        """Получение отфильтрованного списка расписаний"""
        session = get_session()
        query = session.query(Schedule).join(Route)

        # Применяем фильтры, если они указаны
        if from_airport:
            query = query.filter(Route.departure_airport_id == from_airport.id)

        if to_airport:
            query = query.filter(Route.arrival_airport_id == to_airport.id)

        if date:
            query = query.filter(Schedule.date == date)

        if flight_number:
            query = query.filter(Schedule.flight_number.like(f"%{flight_number}%"))

        # Применяем сортировку
        if sort_by == "date_time":
            query = query.order_by(Schedule.date, Schedule.time)
        elif sort_by == "economy_price":
            query = query.order_by(Schedule.economy_price)
        elif sort_by == "confirmed":
            query = query.order_by(Schedule.confirmed.desc())

        return query.all()

    @staticmethod
    def import_schedule_changes(file_content):
        """Импорт изменений расписания из текстового файла"""
        session = get_session()
        results = {
            "success": 0,
            "duplicates": 0,
            "missing_fields": 0
        }

        try:
            # Парсим CSV-файл
            csv_reader = csv.reader(io.StringIO(file_content), delimiter=',')
            header = next(csv_reader)  # Пропускаем заголовок

            for row in csv_reader:
                if len(row) < 7:  # Проверяем, что все необходимые поля присутствуют
                    results["missing_fields"] += 1
                    continue

                operation, flight_number, from_code, to_code, date_str, time_str, price_str = row[:7]

                # Проверяем обязательные поля
                if not all([operation, flight_number, from_code, to_code, date_str, time_str, price_str]):
                    results["missing_fields"] += 1
                    continue

                # Получаем аэропорты
                from_airport = session.query(Airport).filter_by(iata_code=from_code).first()
                to_airport = session.query(Airport).filter_by(iata_code=to_code).first()

                if not from_airport or not to_airport:
                    results["missing_fields"] += 1
                    continue

                # Парсим дату и время
                try:
                    day, month, year = map(int, date_str.split('/'))
                    date = datetime.date(year, month, day)

                    hour, minute = map(int, time_str.split(':'))
                    time = datetime.time(hour, minute)

                    price = float(price_str)
                except (ValueError, IndexError):
                    results["missing_fields"] += 1
                    continue

                # Получаем маршрут
                route = session.query(Route).filter(
                    Route.departure_airport_id == from_airport.id,
                    Route.arrival_airport_id == to_airport.id
                ).first()

                if not route:
                    results["missing_fields"] += 1
                    continue

                # Получаем самолет (берем первый доступный для примера)
                aircraft = session.query(Aircraft).first()
                if not aircraft:
                    results["missing_fields"] += 1
                    continue

                if operation.upper() == "ADD":
                    # Проверяем, существует ли уже такой рейс
                    existing_schedule = session.query(Schedule).filter(
                        Schedule.flight_number == flight_number,
                        Schedule.date == date,
                        Schedule.route_id == route.id
                    ).first()

                    if existing_schedule:
                        results["duplicates"] += 1
                        continue

                    # Создаем новое расписание
                    new_schedule = Schedule(
                        route_id=route.id,
                        aircraft_id=aircraft.id,
                        date=date,
                        time=time,
                        flight_number=flight_number,
                        economy_price=price,
                        confirmed=True
                    )

                    session.add(new_schedule)
                    results["success"] += 1

                elif operation.upper() == "EDIT":
                    # Ищем существующее расписание для редактирования
                    existing_schedule = session.query(Schedule).filter(
                        Schedule.flight_number == flight_number,
                        Schedule.route_id == route.id
                    ).first()

                    if not existing_schedule:
                        results["missing_fields"] += 1
                        continue

                    # Обновляем расписание
                    existing_schedule.date = date
                    existing_schedule.time = time
                    existing_schedule.economy_price = price

                    results["success"] += 1

            session.commit()
            return True, results

        except Exception as e:
            session.rollback()
            return False, str(e)

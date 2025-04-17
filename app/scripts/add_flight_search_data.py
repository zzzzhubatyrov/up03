import sys
import os
import datetime
import random
import string

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.config.database import get_session
from app.models import Country, Airport, Route, Aircraft, Schedule, CabinType, Ticket, User, Role

def add_flight_search_data():
    """Добавление данных для страницы поиска рейсов"""
    session = get_session()
    
    print("Начало добавления данных для поиска рейсов...")
    
    # Проверяем, существует ли страна
    country = session.query(Country).filter_by(name='United Arab Emirates').first()
    if not country:
        country = Country(name='United Arab Emirates')
        session.add(country)
        session.commit()
        print("Добавлена страна: United Arab Emirates")
    
    egypt = session.query(Country).filter_by(name='Egypt').first()
    if not egypt:
        egypt = Country(name='Egypt')
        session.add(egypt)
        session.commit()
        print("Добавлена страна: Egypt")
    
    # Добавляем аэропорты CAI и AUH, если их еще нет
    cai = session.query(Airport).filter_by(iata_code='CAI').first()
    if not cai:
        cai = Airport(
            country_id=egypt.id,
            iata_code='CAI',
            name='Cairo International Airport'
        )
        session.add(cai)
        session.commit()
        print("Добавлен аэропорт: Cairo International Airport (CAI)")
    
    auh = session.query(Airport).filter_by(iata_code='AUH').first()
    if not auh:
        auh = Airport(
            country_id=country.id,
            iata_code='AUH',
            name='Abu Dhabi International Airport'
        )
        session.add(auh)
        session.commit()
        print("Добавлен аэропорт: Abu Dhabi International Airport (AUH)")
    
    # Добавляем маршруты между CAI и AUH, если их еще нет
    route_cai_auh = session.query(Route).filter(
        Route.departure_airport_id == cai.id,
        Route.arrival_airport_id == auh.id
    ).first()
    
    if not route_cai_auh:
        route_cai_auh = Route(
            departure_airport_id=cai.id,
            arrival_airport_id=auh.id,
            distance=2400,  # примерное расстояние в км
            flight_time=180  # примерное время полета в минутах
        )
        session.add(route_cai_auh)
        session.commit()
        print("Добавлен маршрут: CAI -> AUH")
    
    route_auh_cai = session.query(Route).filter(
        Route.departure_airport_id == auh.id,
        Route.arrival_airport_id == cai.id
    ).first()
    
    if not route_auh_cai:
        route_auh_cai = Route(
            departure_airport_id=auh.id,
            arrival_airport_id=cai.id,
            distance=2400,  # примерное расстояние в км
            flight_time=180  # примерное время полета в минутах
        )
        session.add(route_auh_cai)
        session.commit()
        print("Добавлен маршрут: AUH -> CAI")
    
    # Получаем самолет
    aircraft = session.query(Aircraft).first()
    if not aircraft:
        # Если самолетов нет, добавляем новый
        aircraft = Aircraft(
            name='Boeing 737-800',
            make_model='Boeing 737-800',
            total_seats=189,
            economy_seats=162,
            business_seats=27
        )
        session.add(aircraft)
        session.commit()
        print("Добавлен самолет: Boeing 737-800")
    
    # Создаем даты для расписания, как в макете
    dates = [
        datetime.date(2016, 10, 11),  # 11/10/2016
        datetime.date(2016, 10, 13),  # 13/10/2016
        datetime.date(2016, 10, 15),  # 15/10/2016
        datetime.date(2016, 10, 16)   # 16/10/2016
    ]
    
    # Добавляем расписания рейсов
    schedules_added = 0
    
    # Рейсы из AUH в CAI
    for date in dates:
        # Проверяем, существует ли уже такое расписание
        existing_schedule = session.query(Schedule).filter(
            Schedule.route_id == route_auh_cai.id,
            Schedule.date == date
        ).first()
        
        if not existing_schedule:
            # Создаем новое расписание
            schedule = Schedule(
                route_id=route_auh_cai.id,
                aircraft_id=aircraft.id,
                date=date,
                time=datetime.time(8, 15),  # 08:15
                flight_number=f'AA{1000 + dates.index(date)}',
                economy_price=450.0 if date == dates[0] else 450.0,  # Цена как в макете
                confirmed=True
            )
            session.add(schedule)
            schedules_added += 1
    
    # Рейсы из CAI в AUH
    for date in dates:
        # Проверяем, существует ли уже такое расписание
        existing_schedule = session.query(Schedule).filter(
            Schedule.route_id == route_cai_auh.id,
            Schedule.date == date
        ).first()
        
        if not existing_schedule:
            # Создаем новое расписание
            schedule = Schedule(
                route_id=route_cai_auh.id,
                aircraft_id=aircraft.id,
                date=date,
                time=datetime.time(11, 45) if date == dates[2] else datetime.time(8, 15),  # 11:45 для 15/10/2016, 08:15 для остальных
                flight_number=f'AA{2000 + dates.index(date)}',
                economy_price=350.0 if date == dates[3] else 450.0,  # Цена как в макете
                confirmed=True
            )
            session.add(schedule)
            schedules_added += 1
    
    if schedules_added > 0:
        session.commit()
        print(f"Добавлено расписаний: {schedules_added}")
    
    # Получаем типы кабин
    economy = session.query(CabinType).filter_by(name='Economy').first()
    business = session.query(CabinType).filter_by(name='Business').first()
    first_class = session.query(CabinType).filter_by(name='First Class').first()
    
    if not economy or not business or not first_class:
        print("Ошибка: не найдены типы кабин. Пожалуйста, запустите инициализацию базы данных.")
        return
    
    # Получаем пользователя
    user = session.query(User).filter_by(role_id=session.query(Role).filter_by(title='user').first().id).first()
    if not user:
        print("Ошибка: не найден пользователь. Пожалуйста, запустите инициализацию базы данных.")
        return
    
    # Получаем все расписания для маршрутов CAI-AUH и AUH-CAI
    schedules = session.query(Schedule).filter(
        (Schedule.route_id == route_cai_auh.id) | (Schedule.route_id == route_auh_cai.id)
    ).all()
    
    # Добавляем билеты для каждого расписания
    tickets_added = 0
    
    for schedule in schedules:
        # Проверяем, есть ли уже билеты для этого расписания
        existing_tickets = session.query(Ticket).filter_by(schedule_id=schedule.id).count()
        
        if existing_tickets == 0:
            # Генерируем номер бронирования
            booking_reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            
            # Добавляем билеты разных типов
            cabin_types = [economy, business, first_class]
            
            for cabin_type in cabin_types:
                # Добавляем несколько билетов для каждого типа кабины
                for i in range(random.randint(1, 5)):
                    ticket = Ticket(
                        user_id=user.id,
                        schedule_id=schedule.id,
                        cabin_type_id=cabin_type.id,
                        firstname=f'Passenger{i+1}',
                        lastname=f'Test{cabin_type.name}',
                        email=f'passenger{i+1}.{cabin_type.name.lower()}@example.com',
                        phone=f'+1-555-{random.randint(1000, 9999)}',
                        passport_number=f'{cabin_type.name[0]}{random.randint(100000, 999999)}',
                        passport_country_id=country.id,
                        booking_reference=booking_reference,
                        confirmed=True
                    )
                    session.add(ticket)
                    tickets_added += 1
    
    if tickets_added > 0:
        session.commit()
        print(f"Добавлено билетов: {tickets_added}")
    
    print("Данные для поиска рейсов успешно добавлены!")

if __name__ == "__main__":
    add_flight_search_data()

import sys
import os
import datetime
import random

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.config.database import get_session
from app.models import Country, Airport, Route, Aircraft, Schedule

def add_schedule_management_data():
    """Добавление данных для страницы управления расписанием"""
    session = get_session()
    
    print("Начало добавления данных для управления расписанием...")
    
    # Добавляем страны, если их еще нет
    countries = {
        'USA': session.query(Country).filter_by(name='United States').first(),
        'UK': session.query(Country).filter_by(name='United Kingdom').first(),
        'Germany': session.query(Country).filter_by(name='Germany').first(),
        'France': session.query(Country).filter_by(name='France').first(),
        'Spain': session.query(Country).filter_by(name='Spain').first(),
        'Italy': session.query(Country).filter_by(name='Italy').first(),
        'Russia': session.query(Country).filter_by(name='Russia').first(),
        'China': session.query(Country).filter_by(name='China').first(),
        'Japan': session.query(Country).filter_by(name='Japan').first(),
        'Australia': session.query(Country).filter_by(name='Australia').first()
    }
    
    countries_added = 0
    for name, country in countries.items():
        if not country:
            countries[name] = Country(name=name)
            session.add(countries[name])
            countries_added += 1
    
    if countries_added > 0:
        session.commit()
        print(f"Добавлено стран: {countries_added}")
    
    # Добавляем аэропорты, если их еще нет
    airports_data = [
        # Код, Название, Страна
        ('JFK', 'John F. Kennedy International Airport', 'USA'),
        ('LAX', 'Los Angeles International Airport', 'USA'),
        ('ORD', 'O\'Hare International Airport', 'USA'),
        ('LHR', 'London Heathrow Airport', 'UK'),
        ('CDG', 'Charles de Gaulle Airport', 'France'),
        ('FRA', 'Frankfurt Airport', 'Germany'),
        ('MAD', 'Adolfo Suárez Madrid–Barajas Airport', 'Spain'),
        ('FCO', 'Leonardo da Vinci International Airport', 'Italy'),
        ('SVO', 'Sheremetyevo International Airport', 'Russia'),
        ('PEK', 'Beijing Capital International Airport', 'China'),
        ('HND', 'Tokyo Haneda Airport', 'Japan'),
        ('SYD', 'Sydney Airport', 'Australia'),
        ('DXB', 'Dubai International Airport', 'UAE'),
        ('SIN', 'Singapore Changi Airport', 'Singapore'),
        ('AMS', 'Amsterdam Airport Schiphol', 'Netherlands')
    ]
    
    airports = {}
    airports_added = 0
    
    for code, name, country_name in airports_data:
        airport = session.query(Airport).filter_by(iata_code=code).first()
        if not airport:
            # Проверяем, есть ли страна
            country = countries.get(country_name)
            if not country:
                # Если страны нет в словаре, ищем в базе
                country = session.query(Country).filter_by(name=country_name).first()
                if not country:
                    # Если страны нет в базе, создаем новую
                    country = Country(name=country_name)
                    session.add(country)
                    session.commit()
                    print(f"Добавлена страна: {country_name}")
                countries[country_name] = country
            
            # Создаем аэропорт
            airport = Airport(
                country_id=country.id,
                iata_code=code,
                name=name
            )
            session.add(airport)
            airports_added += 1
        
        airports[code] = airport
    
    if airports_added > 0:
        session.commit()
        print(f"Добавлено аэропортов: {airports_added}")
    
    # Добавляем маршруты между аэропортами
    routes_added = 0
    routes = {}
    
    # Создаем маршруты между всеми аэропортами (для простоты)
    airport_codes = list(airports.keys())
    for i in range(len(airport_codes)):
        for j in range(len(airport_codes)):
            if i != j:  # Исключаем маршруты из аэропорта в тот же аэропорт
                from_code = airport_codes[i]
                to_code = airport_codes[j]
                
                # Проверяем, существует ли уже такой маршрут
                route = session.query(Route).filter(
                    Route.departure_airport_id == airports[from_code].id,
                    Route.arrival_airport_id == airports[to_code].id
                ).first()
                
                if not route:
                    # Генерируем случайное расстояние и время полета
                    distance = random.randint(500, 10000)  # км
                    flight_time = distance // 10 + 30  # примерное время в минутах
                    
                    route = Route(
                        departure_airport_id=airports[from_code].id,
                        arrival_airport_id=airports[to_code].id,
                        distance=distance,
                        flight_time=flight_time
                    )
                    session.add(route)
                    routes_added += 1
                
                # Сохраняем маршрут в словарь для дальнейшего использования
                route_key = f"{from_code}-{to_code}"
                routes[route_key] = route
    
    if routes_added > 0:
        session.commit()
        print(f"Добавлено маршрутов: {routes_added}")
    
    # Получаем самолеты
    aircrafts = session.query(Aircraft).all()
    if not aircrafts:
        # Если самолетов нет, добавляем новые
        aircrafts = [
            Aircraft(
                name='Boeing 737-800',
                make_model='Boeing 737-800',
                total_seats=189,
                economy_seats=162,
                business_seats=27
            ),
            Aircraft(
                name='Airbus A320',
                make_model='Airbus A320',
                total_seats=180,
                economy_seats=150,
                business_seats=30
            ),
            Aircraft(
                name='Boeing 777-300ER',
                make_model='Boeing 777-300ER',
                total_seats=396,
                economy_seats=303,
                business_seats=63
            ),
            Aircraft(
                name='Airbus A380',
                make_model='Airbus A380',
                total_seats=615,
                economy_seats=427,
                business_seats=97
            )
        ]
        session.add_all(aircrafts)
        session.commit()
        print(f"Добавлено самолетов: {len(aircrafts)}")
    
    # Создаем расписания рейсов
    schedules_added = 0
    
    # Даты для расписания (текущая дата и следующие 30 дней)
    today = datetime.date.today()
    dates = [today + datetime.timedelta(days=i) for i in range(30)]
    
    # Времена вылета
    departure_times = [
        datetime.time(6, 0),   # 06:00
        datetime.time(8, 30),  # 08:30
        datetime.time(11, 0),  # 11:00
        datetime.time(13, 30), # 13:30
        datetime.time(16, 0),  # 16:00
        datetime.time(18, 30), # 18:30
        datetime.time(21, 0)   # 21:00
    ]
    
    # Создаем расписания для некоторых маршрутов
    route_keys = list(routes.keys())
    selected_routes = random.sample(route_keys, min(50, len(route_keys)))
    
    for route_key in selected_routes:
        from_code, to_code = route_key.split('-')
        
        # Получаем маршрут
        route = routes[route_key]
        if not route.id:
            # Если маршрут только что добавлен, получаем его из базы
            route = session.query(Route).filter(
                Route.departure_airport_id == airports[from_code].id,
                Route.arrival_airport_id == airports[to_code].id
            ).first()
        
        # Выбираем случайный самолет
        aircraft = random.choice(aircrafts)
        
        # Создаем расписания для случайных дат и времен
        for _ in range(random.randint(3, 10)):
            date = random.choice(dates)
            time = random.choice(departure_times)
            
            # Проверяем, существует ли уже такое расписание
            existing_schedule = session.query(Schedule).filter(
                Schedule.route_id == route.id,
                Schedule.date == date,
                Schedule.time == time
            ).first()
            
            if not existing_schedule:
                # Генерируем номер рейса
                flight_number = f"{from_code[0]}{to_code[0]}{random.randint(100, 999)}"
                
                # Генерируем цену эконом-класса
                economy_price = random.randint(100, 1000)
                
                # Определяем, будет ли рейс подтвержден (80% шанс)
                confirmed = random.random() < 0.8
                
                # Создаем расписание
                schedule = Schedule(
                    route_id=route.id,
                    aircraft_id=aircraft.id,
                    date=date,
                    time=time,
                    flight_number=flight_number,
                    economy_price=economy_price,
                    confirmed=confirmed
                )
                session.add(schedule)
                schedules_added += 1
    
    if schedules_added > 0:
        session.commit()
        print(f"Добавлено расписаний: {schedules_added}")
    
    print("Данные для управления расписанием успешно добавлены!")

if __name__ == "__main__":
    add_schedule_management_data()

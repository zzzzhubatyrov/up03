import datetime
import random
import string
from app.config.database import get_session
from app.models import Base, Role, User, Office, Country, CabinType, Aircraft, Airport, Route, Schedule, Ticket

def initialize_database():
    """Инициализация базы данных начальными данными"""
    session = get_session()
    
    # Проверяем, существуют ли роли
    roles = session.query(Role).all()
    if not roles:
        # Добавляем роли
        roles = [
            Role(title='administrator'),
            Role(title='user')
        ]
        session.add_all(roles)
        session.commit()
        print("Roles added successfully")
    
    # Проверяем, существует ли администратор
    admin = session.query(User).filter_by(email='admin@amonic.com').first()
    if not admin:
        # Получаем роль администратора
        admin_role = session.query(Role).filter_by(title='administrator').first()
        
        # Проверяем, существует ли страна
        country = session.query(Country).first()
        if not country:
            country = Country(name='United States')
            session.add(country)
            session.commit()
        
        # Проверяем, существует ли офис
        office = session.query(Office).first()
        if not office:
            office = Office(
                country_id=country.id,
                title='Head Office',
                phone='+1-555-1234',
                contact='John Doe'
            )
            session.add(office)
            session.commit()
        
        # Создаем администратора
        admin = User(
            office_id=office.id,
            role_id=admin_role.id,
            email='admin@amonic.com',
            password='admin',
            firstname='Admin',
            lastname='User',
            birthdate=datetime.datetime(1990, 1, 1),
            active=True
        )
        session.add(admin)
        session.commit()
        print("Admin user added successfully")
    
    # Проверяем, существуют ли типы кабин
    cabin_types = session.query(CabinType).all()
    if not cabin_types:
        # Добавляем типы кабин
        cabin_types = [
            CabinType(name='Economy'),
            CabinType(name='Business'),
            CabinType(name='First Class')
        ]
        session.add_all(cabin_types)
        session.commit()
        print("Cabin types added successfully")
    
    # Проверяем, существуют ли самолеты
    aircrafts = session.query(Aircraft).all()
    if not aircrafts:
        # Добавляем самолеты
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
            )
        ]
        session.add_all(aircrafts)
        session.commit()
        print("Aircrafts added successfully")
    
    # Проверяем, существуют ли аэропорты
    airports = session.query(Airport).all()
    if not airports:
        # Добавляем аэропорты
        airports = [
            Airport(
                country_id=country.id,
                iata_code='JFK',
                name='John F. Kennedy International Airport'
            ),
            Airport(
                country_id=country.id,
                iata_code='LAX',
                name='Los Angeles International Airport'
            ),
            Airport(
                country_id=country.id,
                iata_code='ORD',
                name='O\'Hare International Airport'
            )
        ]
        session.add_all(airports)
        session.commit()
        print("Airports added successfully")
    
    # Проверяем, существуют ли маршруты
    routes = session.query(Route).all()
    if not routes:
        # Получаем аэропорты
        jfk = session.query(Airport).filter_by(iata_code='JFK').first()
        lax = session.query(Airport).filter_by(iata_code='LAX').first()
        ord = session.query(Airport).filter_by(iata_code='ORD').first()
        
        # Добавляем маршруты
        routes = [
            Route(
                departure_airport_id=jfk.id,
                arrival_airport_id=lax.id,
                distance=3983,
                flight_time=360
            ),
            Route(
                departure_airport_id=lax.id,
                arrival_airport_id=jfk.id,
                distance=3983,
                flight_time=360
            ),
            Route(
                departure_airport_id=jfk.id,
                arrival_airport_id=ord.id,
                distance=1189,
                flight_time=150
            ),
            Route(
                departure_airport_id=ord.id,
                arrival_airport_id=jfk.id,
                distance=1189,
                flight_time=150
            )
        ]
        session.add_all(routes)
        session.commit()
        print("Routes added successfully")
    
    # Проверяем, существуют ли расписания
    schedules = session.query(Schedule).all()
    if not schedules:
        # Получаем маршруты и самолеты
        routes = session.query(Route).all()
        boeing = session.query(Aircraft).filter_by(name='Boeing 737-800').first()
        airbus = session.query(Aircraft).filter_by(name='Airbus A320').first()
        
        # Добавляем расписания
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        
        schedules = [
            Schedule(
                route_id=routes[0].id,
                aircraft_id=boeing.id,
                date=today,
                time=datetime.time(8, 0),
                flight_number='AA100',
                economy_price=300.0,
                confirmed=True
            ),
            Schedule(
                route_id=routes[1].id,
                aircraft_id=boeing.id,
                date=tomorrow,
                time=datetime.time(10, 0),
                flight_number='AA101',
                economy_price=320.0,
                confirmed=True
            ),
            Schedule(
                route_id=routes[2].id,
                aircraft_id=airbus.id,
                date=today,
                time=datetime.time(12, 0),
                flight_number='AA200',
                economy_price=200.0,
                confirmed=True
            ),
            Schedule(
                route_id=routes[3].id,
                aircraft_id=airbus.id,
                date=tomorrow,
                time=datetime.time(14, 0),
                flight_number='AA201',
                economy_price=220.0,
                confirmed=True
            )
        ]
        session.add_all(schedules)
        session.commit()
        print("Schedules added successfully")
    
    # Проверяем, существуют ли билеты
    tickets = session.query(Ticket).all()
    if not tickets:
        # Получаем расписания, типы кабин и пользователей
        schedules = session.query(Schedule).all()
        economy = session.query(CabinType).filter_by(name='Economy').first()
        business = session.query(CabinType).filter_by(name='Business').first()
        user = session.query(User).filter_by(role_id=session.query(Role).filter_by(title='user').first().id).first()
        
        # Если нет обычного пользователя, создаем его
        if not user:
            user_role = session.query(Role).filter_by(title='user').first()
            office = session.query(Office).first()
            
            user = User(
                office_id=office.id,
                role_id=user_role.id,
                email='user@amonic.com',
                password='user',
                firstname='Regular',
                lastname='User',
                birthdate=datetime.datetime(1995, 5, 5),
                active=True
            )
            session.add(user)
            session.commit()
        
        # Добавляем билеты
        booking_reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        tickets = [
            Ticket(
                user_id=user.id,
                schedule_id=schedules[0].id,
                cabin_type_id=economy.id,
                firstname='John',
                lastname='Doe',
                email='john.doe@example.com',
                phone='+1-555-6789',
                passport_number='AB123456',
                passport_country_id=session.query(Country).first().id,
                booking_reference=booking_reference,
                confirmed=True
            ),
            Ticket(
                user_id=user.id,
                schedule_id=schedules[0].id,
                cabin_type_id=business.id,
                firstname='Jane',
                lastname='Smith',
                email='jane.smith@example.com',
                phone='+1-555-9876',
                passport_number='CD789012',
                passport_country_id=session.query(Country).first().id,
                booking_reference=booking_reference,
                confirmed=True
            )
        ]
        session.add_all(tickets)
        session.commit()
        print("Tickets added successfully")
    
    print("Database initialization completed successfully")

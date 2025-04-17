from sqlalchemy import Column, Integer, String, Date, Time, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Aircraft(Base):
    __tablename__ = 'aircrafts'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    make_model = Column(String(100), nullable=False)
    total_seats = Column(Integer, nullable=False)
    economy_seats = Column(Integer, nullable=False)
    business_seats = Column(Integer, nullable=False)

    schedules = relationship('Schedule', back_populates='aircraft')

class Airport(Base):
    __tablename__ = 'airports'
    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey('countries.id'))
    iata_code = Column(String(3), nullable=False, unique=True)
    name = Column(String(100), nullable=False)

    country = relationship('Country', back_populates='airports')
    departure_routes = relationship('Route', foreign_keys='Route.departure_airport_id', back_populates='departure_airport')
    arrival_routes = relationship('Route', foreign_keys='Route.arrival_airport_id', back_populates='arrival_airport')

class Route(Base):
    __tablename__ = 'routes'
    id = Column(Integer, primary_key=True)
    departure_airport_id = Column(Integer, ForeignKey('airports.id'))
    arrival_airport_id = Column(Integer, ForeignKey('airports.id'))
    distance = Column(Integer, nullable=False)  # в километрах
    flight_time = Column(Integer, nullable=False)  # в минутах

    departure_airport = relationship('Airport', foreign_keys=[departure_airport_id], back_populates='departure_routes')
    arrival_airport = relationship('Airport', foreign_keys=[arrival_airport_id], back_populates='arrival_routes')
    schedules = relationship('Schedule', back_populates='route')

class CabinType(Base):
    __tablename__ = 'cabin_types'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    tickets = relationship('Ticket', back_populates='cabin_type')

class Schedule(Base):
    __tablename__ = 'schedules'
    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey('routes.id'))
    aircraft_id = Column(Integer, ForeignKey('aircrafts.id'))
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    flight_number = Column(String(10), nullable=False)
    economy_price = Column(Float, nullable=False)
    confirmed = Column(Boolean, default=True)

    route = relationship('Route', back_populates='schedules')
    aircraft = relationship('Aircraft', back_populates='schedules')
    tickets = relationship('Ticket', back_populates='schedule')

    @property
    def business_price(self):
        # Бизнес-класс на 35% дороже эконом-класса
        return int(self.economy_price * 1.35)

    @property
    def first_class_price(self):
        # Первый класс на 30% дороже бизнес-класса
        return int(self.business_price * 1.3)

    def get_price_by_cabin_type(self, cabin_type_name):
        """Get price based on cabin type name"""
        if cabin_type_name.lower() == 'economy':
            return self.economy_price
        elif cabin_type_name.lower() == 'business':
            return self.business_price
        elif cabin_type_name.lower() == 'first class':
            return self.first_class_price
        else:
            return self.economy_price  # Default to economy price

class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    schedule_id = Column(Integer, ForeignKey('schedules.id'))
    cabin_type_id = Column(Integer, ForeignKey('cabin_types.id'))
    firstname = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    passport_number = Column(String(20), nullable=False)
    passport_country_id = Column(Integer, ForeignKey('countries.id'))
    booking_reference = Column(String(10), nullable=False)
    confirmed = Column(Boolean, default=False)

    user = relationship('User', back_populates='tickets')
    schedule = relationship('Schedule', back_populates='tickets')
    cabin_type = relationship('CabinType', back_populates='tickets')
    passport_country = relationship('Country')

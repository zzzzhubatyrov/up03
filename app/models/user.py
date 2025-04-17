from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    users = relationship('User', back_populates='role')

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    office_id = Column(Integer, ForeignKey('offices.id'))
    role_id = Column(Integer, ForeignKey('roles.id'))
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    firstname = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    birthdate = Column(DateTime, nullable=False)
    active = Column(Boolean, default=True)

    office = relationship('Office', back_populates='users')
    role = relationship('Role', back_populates='users')
    sessions = relationship('UserSession', back_populates='user')
    crashes = relationship('SystemCrash', back_populates='user')
    tickets = relationship('Ticket', back_populates='user')

class Office(Base):
    __tablename__ = 'offices'
    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey('countries.id'))
    title = Column(String(100), nullable=False)
    phone = Column(String(20))
    contact = Column(String(100))

    country = relationship('Country', back_populates='offices')
    users = relationship('User', back_populates='office')

class Country(Base):
    __tablename__ = 'countries'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    offices = relationship('Office', back_populates='country')
    airports = relationship('Airport', back_populates='country')

class LoginAttempt(Base):
    __tablename__ = 'login_attempts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    timestamp = Column(DateTime, nullable=False)
    success = Column(Boolean, default=False)
    error_message = Column(String(200))

class UserSession(Base):
    __tablename__ = 'user_sessions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    login_time = Column(DateTime, nullable=False)
    logout_time = Column(DateTime, nullable=True)
    crash = Column(Boolean, default=False)
    crash_reason = Column(String(200), nullable=True)

    user = relationship('User', back_populates='sessions')

    def get_time_spent(self):
        if self.logout_time:
            return self.logout_time - self.login_time
        return None

class SystemCrash(Base):
    __tablename__ = 'system_crashes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    timestamp = Column(DateTime, nullable=False)
    reason = Column(String(200), nullable=False)

    user = relationship('User', back_populates='crashes')

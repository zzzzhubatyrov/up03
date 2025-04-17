from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base

import os

# Конфигурация базы данных
# Создаем путь к базе данных в корневой директории проекта
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
DATABASE_URL = f'sqlite:///{os.path.join(BASE_DIR, "amonic.db")}'

def get_engine():
    """Создает и возвращает движок SQLAlchemy"""
    return create_engine(DATABASE_URL)

def get_session():
    """Создает и возвращает сессию SQLAlchemy"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def init_db():
    """Инициализирует базу данных, создавая все таблицы"""
    engine = get_engine()
    Base.metadata.create_all(engine)

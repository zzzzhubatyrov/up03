# Инициализация пакета моделей
from app.models.base import Base
from app.models.user import Role, User, Office, Country, LoginAttempt, UserSession, SystemCrash
from app.models.flight import Aircraft, Airport, Route, CabinType, Schedule, Ticket

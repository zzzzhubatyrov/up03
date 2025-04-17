import re
import datetime

def validate_email(email):
    """Проверка корректности email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password, min_length=6):
    """Проверка корректности пароля"""
    return len(password) >= min_length

def validate_date_format(date_str, format="%d/%m/%Y"):
    """Проверка корректности формата даты"""
    try:
        datetime.datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False

def validate_time_format(time_str, format="%H:%M"):
    """Проверка корректности формата времени"""
    try:
        datetime.datetime.strptime(time_str, format)
        return True
    except ValueError:
        return False

def validate_positive_number(value):
    """Проверка, что значение является положительным числом"""
    try:
        num = float(value)
        return num > 0
    except (ValueError, TypeError):
        return False

def validate_iata_code(code):
    """Проверка корректности IATA-кода аэропорта"""
    pattern = r'^[A-Z]{3}$'
    return bool(re.match(pattern, code))

def validate_flight_number(number):
    """Проверка корректности номера рейса"""
    pattern = r'^[A-Z0-9]{2,8}$'
    return bool(re.match(pattern, number))

def validate_passport_number(number):
    """Проверка корректности номера паспорта"""
    pattern = r'^[A-Z0-9]{6,12}$'
    return bool(re.match(pattern, number))

import datetime

def parse_date(date_str, format="%d/%m/%Y"):
    """Парсинг строки даты в объект datetime.date"""
    try:
        return datetime.datetime.strptime(date_str, format).date()
    except ValueError:
        return None

def format_date(date, format="%d/%m/%Y"):
    """Форматирование объекта datetime.date в строку"""
    if isinstance(date, datetime.datetime):
        return date.strftime(format)
    elif isinstance(date, datetime.date):
        return date.strftime(format)
    return ""

def format_time(time, format="%H:%M"):
    """Форматирование объекта datetime.time в строку"""
    if isinstance(time, datetime.time):
        return time.strftime(format)
    elif isinstance(time, datetime.datetime):
        return time.strftime(format)
    return ""

def format_duration(seconds):
    """Форматирование длительности в секундах в строку формата HH:MM:SS"""
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_date_range(date, days_before=0, days_after=0):
    """Получение диапазона дат"""
    start_date = date - datetime.timedelta(days=days_before)
    end_date = date + datetime.timedelta(days=days_after)
    return start_date, end_date

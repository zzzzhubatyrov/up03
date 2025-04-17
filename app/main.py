import sys
import os

# Добавляем родительскую директорию в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config.database import init_db
from app.config.init_db import initialize_database
from app.views.login_view import LoginView

def main():
    """Главная функция приложения"""
    # Инициализируем базу данных
    init_db()

    # Инициализируем начальные данные
    initialize_database()

    # Запускаем окно входа
    app = LoginView()
    app.mainloop()

if __name__ == "__main__":
    main()

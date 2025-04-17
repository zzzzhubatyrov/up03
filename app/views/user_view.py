import tkinter as tk
from tkinter import ttk
import datetime
from datetime import timedelta
from sqlalchemy import func
from app.config.database import get_session
from app.models import UserSession, SystemCrash
from app.controllers.user_controller import UserController
# Импортируем внутри методов, чтобы избежать циклических импортов

class UserView(tk.Toplevel):
    """Окно пользователя"""

    def __init__(self, user, user_session):
        super().__init__()

        self.user = user
        self.user_session = user_session

        self.title("AMONIC Airlines Automation System")
        self.geometry("800x600")

        # Создаем интерфейс
        self.create_menu()
        self.create_info_panel()
        self.create_activity_table()

        # Загружаем данные
        self.load_activity_data()

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Создаем подменю для рейсов
        flight_menu = tk.Menu(menubar, tearoff=0)
        flight_menu.add_command(label="Search Flights", command=self.open_flight_search)

        # Добавляем подменю в главное меню
        menubar.add_cascade(label="Flights", menu=flight_menu)

        # Добавляем пункт Exit
        menubar.add_command(label="Exit", command=self.quit)

    def create_info_panel(self):
        """Создание информационной панели пользователя"""
        # Создаем фрейм для информационной панели
        info_frame = ttk.LabelFrame(self, text="User Information")
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        # Приветственное сообщение с именем пользователя
        welcome_label = ttk.Label(info_frame, text=f"Welcome, {self.user.firstname} {self.user.lastname}!",
                                  font=("Arial", 14, "bold"))
        welcome_label.pack(anchor=tk.W, padx=10, pady=10)

        # Время, проведенное в системе за последние 30 дней
        time_spent = self.calculate_time_spent()
        time_label = ttk.Label(info_frame, text=f"Time spent on system: {time_spent}")
        time_label.pack(anchor=tk.W, padx=10, pady=5)

        # Количество сбоев
        crashes = self.count_crashes()
        crash_label = ttk.Label(info_frame, text=f"Number of crashes: {crashes}")
        crash_label.pack(anchor=tk.W, padx=10, pady=5)

    def create_activity_table(self):
        """Создание таблицы активности пользователя"""
        # Создаем фрейм для таблицы активности
        activity_frame = ttk.LabelFrame(self, text="Your Activities")
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Создаем таблицу
        columns = ("Login Date", "Login Time", "Logout Time", "Time Spent", "Crash")
        self.activity_tree = ttk.Treeview(activity_frame, columns=columns, show='headings')

        # Настройка столбцов
        for col in columns:
            self.activity_tree.heading(col, text=col)
            if col == "Time Spent":
                self.activity_tree.column(col, width=150, anchor=tk.CENTER)
            elif col == "Crash":
                self.activity_tree.column(col, width=100, anchor=tk.CENTER)
            else:
                self.activity_tree.column(col, width=120, anchor=tk.CENTER)

        # Добавляем полосы прокрутки
        scrollbar_y = ttk.Scrollbar(activity_frame, orient=tk.VERTICAL, command=self.activity_tree.yview)
        self.activity_tree.configure(yscrollcommand=scrollbar_y.set)

        # Размещаем таблицу и полосы прокрутки
        self.activity_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Настраиваем теги для отображения сбоев
        self.activity_tree.tag_configure('crash', background='#ffcccc')

    def load_activity_data(self):
        """Загрузка данных активности пользователя"""
        # Очищаем таблицу
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)

        # Получаем сессии пользователя
        session = get_session()
        user_sessions = session.query(UserSession).filter_by(user_id=self.user.id).order_by(UserSession.login_time.desc()).all()

        # Добавляем сессии в таблицу
        for user_session in user_sessions:
            # Форматируем дату и время входа
            login_date = user_session.login_time.strftime("%d/%m/%Y")
            login_time = user_session.login_time.strftime("%H:%M:%S")

            # Форматируем время выхода (если есть)
            logout_time = user_session.logout_time.strftime("%H:%M:%S") if user_session.logout_time else "Active"

            # Рассчитываем время, проведенное в системе
            time_spent = "Active" if not user_session.logout_time else self.format_time_delta(user_session.logout_time - user_session.login_time)

            # Определяем, был ли сбой
            crash_status = "Yes" if user_session.crash else "No"

            # Определяем тег для строки (красный для сессий со сбоем)
            tags = ('crash',) if user_session.crash else ()

            # Добавляем строку в таблицу
            self.activity_tree.insert("", tk.END, values=(
                login_date,
                login_time,
                logout_time,
                time_spent,
                crash_status
            ), tags=tags)

    def calculate_time_spent(self):
        """Расчет времени, проведенного в системе за последние 30 дней"""
        session = get_session()

        # Определяем дату 30 дней назад
        thirty_days_ago = datetime.datetime.now() - timedelta(days=30)

        # Получаем все сессии пользователя за последние 30 дней
        user_sessions = session.query(UserSession).filter(
            UserSession.user_id == self.user.id,
            UserSession.login_time >= thirty_days_ago
        ).all()

        # Рассчитываем общее время
        total_seconds = 0
        for user_session in user_sessions:
            if user_session.logout_time:
                # Если сессия завершена, добавляем время между входом и выходом
                delta = user_session.logout_time - user_session.login_time
                total_seconds += delta.total_seconds()
            else:
                # Если сессия активна, добавляем время от входа до текущего момента
                delta = datetime.datetime.now() - user_session.login_time
                total_seconds += delta.total_seconds()

        # Форматируем результат
        return self.format_time_delta(timedelta(seconds=total_seconds))

    def count_crashes(self):
        """Подсчет количества сбоев системы для текущего пользователя"""
        session = get_session()

        # Считаем количество сбоев из таблицы system_crashes
        crash_count = session.query(func.count(SystemCrash.id)).filter(
            SystemCrash.user_id == self.user.id
        ).scalar() or 0

        # Считаем количество сбоев из таблицы user_sessions
        session_crash_count = session.query(func.count(UserSession.id)).filter(
            UserSession.user_id == self.user.id,
            UserSession.crash == True
        ).scalar() or 0

        # Возвращаем общее количество сбоев
        return crash_count + session_crash_count

    def format_time_delta(self, delta):
        """Форматирование временного интервала в читаемый вид"""
        # Получаем общее количество секунд
        total_seconds = int(delta.total_seconds())

        # Рассчитываем часы, минуты и секунды
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Форматируем результат
        if hours > 0:
            return f"{hours} hours {minutes} minutes"
        elif minutes > 0:
            return f"{minutes} minutes {seconds} seconds"
        else:
            return f"{seconds} seconds"

    def open_flight_search(self):
        """Открытие окна поиска рейсов"""
        from app.views.flight_search_view import FlightSearchView
        FlightSearchView(self, self.user)

    def quit(self):
        """Выход из приложения с закрытием сессии"""
        # Закрываем сессию пользователя
        UserController.close_session(self.user_session)

        # Закрываем окно
        self.destroy()

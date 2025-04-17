import tkinter as tk
from tkinter import messagebox
import datetime
from app.controllers.user_controller import UserController
# Импортируем представления внутри методов, чтобы избежать циклических импортов

class LoginView(tk.Tk):
    """Окно входа в систему"""

    def __init__(self):
        super().__init__()

        self.login_attempts = 0
        self.last_attempt_time = None

        self.title("Login")
        self.geometry("400x300")

        # Создаем интерфейс
        self.create_widgets()

    def create_widgets(self):
        # Логотип
        # Здесь должна быть загрузка логотипа AMONIC

        # Поле для имени пользователя
        tk.Label(self, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.pack(pady=5)

        # Поле для пароля
        tk.Label(self, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=5)

        # Фрейм для кнопок
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Login", command=self.login).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Exit", command=self.quit).pack(side=tk.LEFT)

        # Метка для таймера
        self.timer_label = tk.Label(self, text="")
        self.timer_label.pack(pady=10)

    def login(self):
        """Обработка входа в систему"""
        if self.login_attempts >= 3:
            if datetime.datetime.now() - self.last_attempt_time < datetime.timedelta(seconds=10):
                remaining = 10 - (datetime.datetime.now() - self.last_attempt_time).seconds
                self.timer_label.config(text=f"Пожалуйста, подождите {remaining} секунд")
                self.after(1000, self.update_timer)
                return
            else:
                self.login_attempts = 0
                self.timer_label.config(text="")

        email = self.username_entry.get()
        password = self.password_entry.get()

        # Аутентификация пользователя
        user, message = UserController.authenticate(email, password)

        if user:
            # Открываем соответствующее окно в зависимости от роли
            self.open_main_window(user, message)
        else:
            self.login_attempts += 1
            self.last_attempt_time = datetime.datetime.now()
            messagebox.showerror("Error", message)

    def update_timer(self):
        """Обновление таймера блокировки"""
        if self.login_attempts >= 3:
            remaining = 10 - (datetime.datetime.now() - self.last_attempt_time).seconds
            if remaining > 0:
                self.timer_label.config(text=f"Пожалуйста, подождите {remaining} секунд")
                self.after(1000, self.update_timer)
            else:
                self.timer_label.config(text="")
                self.login_attempts = 0

    def open_main_window(self, user, user_session):
        """Открытие главного окна в зависимости от роли пользователя"""
        # Импортируем здесь, чтобы избежать циклических импортов
        from app.views.admin_view import AdminView
        from app.views.user_view import UserView

        self.withdraw()  # Скрываем окно входа

        if user.role.title == "administrator":
            # Открываем окно администратора
            admin_window = AdminView(user, user_session)
            admin_window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(user_session))
        else:
            # Открываем окно пользователя
            user_window = UserView(user, user_session)
            user_window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(user_session))

    def on_closing(self, user_session):
        """Обработка закрытия окна"""
        # Закрываем сеанс пользователя
        UserController.close_session(user_session)
        self.quit()

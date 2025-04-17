import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import re
from app.controllers.user_controller import UserController
from app.models import Office, Role

class AddUserWindow(tk.Toplevel):
    """Окно добавления нового пользователя"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Настройка окна
        self.title("Add user")
        self.geometry("400x400")
        self.resizable(False, False)

        # Делаем окно модальным
        self.transient(parent)
        self.grab_set()

        # Центрируем окно относительно родительского
        self.center_window()

        # Инициализируем переменные для полей ввода
        self.email_var = tk.StringVar()
        self.firstname_var = tk.StringVar()
        self.lastname_var = tk.StringVar()
        self.office_var = tk.StringVar()
        self.birthdate_var = tk.StringVar()
        self.password_var = tk.StringVar()

        # Создаем интерфейс
        self.create_widgets()

        # Устанавливаем фокус на первое поле
        self.email_entry.focus_set()

    def center_window(self):
        """Центрирование окна относительно родительского"""
        self.update_idletasks()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()

        width = self.winfo_width()
        height = self.winfo_height()

        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2

        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Основной контейнер с отступами
        main_frame = ttk.Frame(self, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Создаем и размещаем элементы формы
        # Email
        ttk.Label(main_frame, text="Email address").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        self.email_entry = ttk.Entry(main_frame, width=30, textvariable=self.email_var)
        self.email_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 10))

        # First name
        ttk.Label(main_frame, text="First name").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        self.firstname_entry = ttk.Entry(main_frame, width=30, textvariable=self.firstname_var)
        self.firstname_entry.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))

        # Last name
        ttk.Label(main_frame, text="Last name").grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        self.lastname_entry = ttk.Entry(main_frame, width=30, textvariable=self.lastname_var)
        self.lastname_entry.grid(row=2, column=1, sticky=tk.W, pady=(0, 10))

        # Office
        ttk.Label(main_frame, text="Office").grid(row=3, column=0, sticky=tk.W, pady=(0, 10))

        # Получаем список офисов
        offices = UserController.get_all_offices()
        office_names = [office.title for office in offices]

        self.office_combo = ttk.Combobox(main_frame, width=27, textvariable=self.office_var, values=office_names, state="readonly")
        if office_names:
            self.office_combo.current(0)  # Выбираем первый офис по умолчанию
        self.office_combo.grid(row=3, column=1, sticky=tk.W, pady=(0, 10))

        # Birthdate
        ttk.Label(main_frame, text="Birthdate").grid(row=4, column=0, sticky=tk.W, pady=(0, 10))
        self.birthdate_entry = ttk.Entry(main_frame, width=30, textvariable=self.birthdate_var)
        self.birthdate_entry.grid(row=4, column=1, sticky=tk.W, pady=(0, 10))
        self.birthdate_entry.insert(0, "[dd/mm/yy]")
        self.birthdate_entry.bind("<FocusIn>", self.clear_birthdate_placeholder)
        self.birthdate_entry.bind("<FocusOut>", self.restore_birthdate_placeholder)

        # Password
        ttk.Label(main_frame, text="Password").grid(row=5, column=0, sticky=tk.W, pady=(0, 10))
        self.password_entry = ttk.Entry(main_frame, width=30, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=5, column=1, sticky=tk.W, pady=(0, 10))

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(button_frame, text="Save", command=self.save_user, width=15).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.destroy, width=15).grid(row=0, column=1)

    def clear_birthdate_placeholder(self, event):
        """Очистка плейсхолдера даты рождения при фокусе"""
        if self.birthdate_var.get() == "[dd/mm/yy]":
            self.birthdate_var.set("")

    def restore_birthdate_placeholder(self, event):
        """Восстановление плейсхолдера даты рождения при потере фокуса"""
        if not self.birthdate_var.get():
            self.birthdate_var.set("[dd/mm/yy]")

    def validate_email(self, email):
        """Проверка корректности email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_birthdate(self, birthdate):
        """Проверка корректности даты рождения"""
        if birthdate == "[dd/mm/yy]":
            return False

        try:
            # Проверяем формат даты
            day, month, year = map(int, birthdate.split('/'))

            # Добавляем 2000 к году, если он меньше 100
            if year < 100:
                year += 2000

            # Проверяем валидность даты
            date = datetime.date(year, month, day)

            # Проверяем, что дата не в будущем
            if date > datetime.date.today():
                return False

            return date
        except (ValueError, TypeError):
            return False

    def save_user(self):
        """Сохранение нового пользователя"""
        # Получаем данные из полей ввода
        email = self.email_var.get().strip()
        firstname = self.firstname_var.get().strip()
        lastname = self.lastname_var.get().strip()
        office = self.office_var.get()
        birthdate = self.birthdate_var.get().strip()
        password = self.password_var.get()

        # Проверяем обязательные поля
        if not email or not firstname or not lastname or not office or not password:
            messagebox.showerror("Error", "All fields except birthdate are required")
            return

        # Проверяем корректность email
        if not self.validate_email(email):
            messagebox.showerror("Error", "Invalid email format")
            return

        # Проверяем дату рождения, если она указана
        birthdate_obj = None
        if birthdate and birthdate != "[dd/mm/yy]":
            birthdate_obj = self.validate_birthdate(birthdate)
            if not birthdate_obj:
                messagebox.showerror("Error", "Invalid birthdate format. Use dd/mm/yy")
                return

        # Создаем пользователя
        success, message = UserController.add_user(
            email=email,
            firstname=firstname,
            lastname=lastname,
            office_title=office,
            birthdate=birthdate_obj,
            password=password,
            role_title="user"  # По умолчанию создаем обычного пользователя
        )

        if success:
            messagebox.showinfo("Success", "User added successfully")
            self.destroy()  # Закрываем окно после успешного добавления
        else:
            messagebox.showerror("Error", message)

    def on_closing(self, user_session):
        """"""
        # Close session
        UserController.close_session(user_session)
        self.quit()
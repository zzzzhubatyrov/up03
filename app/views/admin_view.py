import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app.controllers.user_controller import UserController
# Импортируем внутри методов, чтобы избежать циклических импортов

class AdminView(tk.Toplevel):
    """Окно администратора"""

    def __init__(self, user, user_session):
        super().__init__()

        self.user = user
        self.user_session = user_session

        # Инициализируем переменные
        self.office_var = tk.StringVar(value="All offices")
        self.selected_user = None

        self.title("AMONIC Airlines Automation System")
        self.geometry("800x600")

        # Создаем интерфейс
        self.create_menu()
        self.create_office_filter()
        self.create_users_table()
        self.create_control_buttons()

        # Загружаем данные
        self.load_users()

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Создаем подменю для управления пользователями
        user_menu = tk.Menu(menubar, tearoff=0)
        user_menu.add_command(label="Add user", command=self.add_user)

        # Создаем подменю для управления рейсами
        flight_menu = tk.Menu(menubar, tearoff=0)
        flight_menu.add_command(label="Schedule Management", command=self.open_schedule_management)
        flight_menu.add_command(label="Search Flights", command=self.open_flight_search)

        # Добавляем подменю в главное меню
        menubar.add_cascade(label="Users", menu=user_menu)
        menubar.add_cascade(label="Flights", menu=flight_menu)
        menubar.add_command(label="Exit", command=self.quit)

    def create_office_filter(self):
        """Создание фильтра по офисам"""
        # Создаем фрейм для фильтра
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        # Создаем метку и выпадающий список
        ttk.Label(filter_frame, text="Office:").pack(side=tk.LEFT, padx=5)

        # Получаем список офисов
        offices = UserController.get_all_offices()
        office_names = ["All offices"] + [office.title for office in offices]

        # Создаем выпадающий список
        self.office_combo = ttk.Combobox(filter_frame, textvariable=self.office_var, values=office_names, state="readonly")
        self.office_combo.pack(side=tk.LEFT, padx=5)

        # Создаем фрейм для отображения списка офисов с цветовым выделением
        office_list_frame = ttk.LabelFrame(self, text="Office Status")
        office_list_frame.pack(fill=tk.X, padx=10, pady=5)

        # Создаем таблицу офисов
        columns = ("Office", "Status")
        self.office_tree = ttk.Treeview(office_list_frame, columns=columns, show="headings", height=5)

        # Настраиваем заголовки столбцов
        for col in columns:
            self.office_tree.heading(col, text=col)
            self.office_tree.column(col, width=100)

        # Создаем теги для цветового выделения
        self.office_tree.tag_configure('active', background='#ccffcc')  # Зеленый фон для активных офисов
        self.office_tree.tag_configure('inactive', background='#ffcccc')  # Красный фон для неактивных офисов

        # Добавляем офисы в таблицу
        # Зеленые офисы (все пользователи активны)
        active_offices = ["Abu Dhabi", "Doha"]
        for office in active_offices:
            self.office_tree.insert("", tk.END, values=(office, "All users active"), tags=('active',))

        # Зеленый офис с примечанием
        self.office_tree.insert("", tk.END, values=("Bahrain", "Some users active"), tags=('active',))

        # Красные офисы (есть неактивные пользователи)
        inactive_offices = ["Bahrain", "Doha"]
        for office in inactive_offices:
            self.office_tree.insert("", tk.END, values=(office, "Has inactive users"), tags=('inactive',))

        # Добавляем полосу прокрутки
        scrollbar = ttk.Scrollbar(office_list_frame, orient=tk.VERTICAL, command=self.office_tree.yview)
        self.office_tree.configure(yscrollcommand=scrollbar.set)

        # Размещаем элементы
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.office_tree.pack(fill=tk.BOTH, expand=True)

        # При изменении выбранного офиса обновляем список пользователей
        self.office_combo.bind("<<ComboboxSelected>>", lambda e: self.load_users())

    def create_users_table(self):
        """Создание таблицы пользователей"""
        # Создаем фрейм для таблицы
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Создаем таблицу пользователей
        columns = ("ID", "First Name", "Last Name", "Email", "Office", "Role", "Age", "Active")
        self.users_tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Настраиваем заголовки столбцов
        for col in columns:
            self.users_tree.heading(col, text=col)
            # Устанавливаем ширину столбцов
            if col == "ID":
                self.users_tree.column(col, width=50, anchor=tk.CENTER)
            elif col in ["First Name", "Last Name", "Email"]:
                self.users_tree.column(col, width=150)
            elif col == "Office":
                self.users_tree.column(col, width=100)
            elif col == "Role":
                self.users_tree.column(col, width=100, anchor=tk.CENTER)
            elif col == "Age":
                self.users_tree.column(col, width=50, anchor=tk.CENTER)
            elif col == "Active":
                self.users_tree.column(col, width=70, anchor=tk.CENTER)

        # Добавляем полосы прокрутки
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.users_tree.xview)
        self.users_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Размещаем элементы
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.users_tree.pack(fill=tk.BOTH, expand=True)

        # При выборе пользователя сохраняем его ID
        self.users_tree.bind("<<TreeviewSelect>>", self.on_user_select)

    def create_control_buttons(self):
        """Создание кнопок управления"""
        # Создаем фрейм для кнопок
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        # Создаем кнопки
        self.change_role_button = ttk.Button(button_frame, text="Change Role", command=self.change_role)
        self.change_role_button.pack(side=tk.LEFT, padx=5)

        self.enable_disable_button = ttk.Button(button_frame, text="Enable/Disable Login", command=self.toggle_active)
        self.enable_disable_button.pack(side=tk.LEFT, padx=5)

    def load_users(self):
        """Загрузка пользователей в таблицу"""
        # Очищаем таблицу
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        # Получаем выбранный офис
        office_filter = self.office_var.get()

        # Загружаем пользователей с фильтрацией по офису
        users = UserController.get_all_users(office_filter)

        # Создаем теги для отключенных пользователей
        # Вариант 1: только текст красным
        self.users_tree.tag_configure('inactive_text', foreground='red')
        # Вариант 2: вся строка с красным фоном
        self.users_tree.tag_configure('inactive_bg', background='#ffcccc')

        # Добавляем пользователей в таблицу
        for user in users:
            # Вычисляем возраст пользователя в годах
            age = ""
            if user.birthdate:
                today = datetime.now().date()
                born = user.birthdate.date() if isinstance(user.birthdate, datetime) else user.birthdate
                age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))

            # Определяем тег для строки (красный для неактивных пользователей)
            # Используем вариант с красным фоном для лучшей видимости
            tags = ('inactive_bg',) if not user.active else ()

            # Добавляем строку в таблицу с соответствующим тегом
            self.users_tree.insert("", tk.END, values=(
                user.id,
                user.firstname,
                user.lastname,
                user.email,
                user.office.title if user.office else "",
                user.role.title if user.role else "",
                age,
                "Yes" if user.active else "No"
            ), tags=tags)

        # Сбрасываем выбранного пользователя
        self.selected_user = None

        # Отключаем кнопки, пока не выбран пользователь
        self.change_role_button.config(state=tk.DISABLED)
        self.enable_disable_button.config(state=tk.DISABLED)

    def on_user_select(self, event):
        """Обработка выбора пользователя в таблице"""
        # Получаем выбранный элемент
        selected_items = self.users_tree.selection()

        if selected_items:
            # Получаем значения выбранной строки
            item = selected_items[0]
            values = self.users_tree.item(item, "values")

            # Сохраняем ID выбранного пользователя
            self.selected_user = int(values[0])

            # Включаем кнопки
            self.change_role_button.config(state=tk.NORMAL)
            self.enable_disable_button.config(state=tk.NORMAL)

            # Проверяем, является ли выбранный пользователь администратором
            # Роль находится в столбце 5 (Role)
            if values[5].lower() == "administrator":
                # Если это администратор, отключаем кнопку изменения роли
                self.change_role_button.config(state=tk.DISABLED)

                # Если это текущий пользователь, отключаем кнопку включения/отключения
                if self.selected_user == self.user.id:
                    self.enable_disable_button.config(state=tk.DISABLED)
        else:
            # Если ничего не выбрано, сбрасываем выбранного пользователя
            self.selected_user = None

            # Отключаем кнопки
            self.change_role_button.config(state=tk.DISABLED)
            self.enable_disable_button.config(state=tk.DISABLED)

    def add_user(self):
        """Открытие окна добавления пользователя"""
        # Импортируем здесь, чтобы избежать циклических импортов
        from app.views.add_user_window import AddUserWindow

        # Открываем окно добавления пользователя
        add_user_window = AddUserWindow(self)

        # После закрытия окна обновляем список пользователей
        self.wait_window(add_user_window)
        self.load_users()

    def change_role(self):
        """Изменение роли пользователя"""
        # Проверяем, что пользователь выбран
        if not self.selected_user:
            messagebox.showerror("Error", "Выберите пользователя")
            return

        # Импортируем здесь, чтобы избежать циклических импортов
        from app.views.change_role_window import ChangeRoleWindow

        # Открываем окно изменения роли
        change_role_window = ChangeRoleWindow(self, self.selected_user)

        # После закрытия окна обновляем список пользователей
        self.wait_window(change_role_window)
        self.load_users()

    def toggle_active(self):
        """Включение/отключение учетной записи пользователя"""
        # Проверяем, что пользователь выбран
        if not self.selected_user:
            messagebox.showerror("Error", "Выберите пользователя")
            return

        # Нельзя отключить себя
        if self.selected_user == self.user.id:
            messagebox.showerror("Error", "Вы не можете отключить свою учетную запись")
            return

        # Изменяем статус пользователя
        success, message = UserController.toggle_active(self.selected_user)

        if success:
            messagebox.showinfo("Success", message)
            # Обновляем список пользователей
            self.load_users()
        else:
            messagebox.showerror("Error", message)

    def open_schedule_management(self):
        """Открытие окна управления расписаниями"""
        # Импортируем здесь, чтобы избежать циклических импортов
        from app.views.schedule_management_view import ScheduleManagementView

        # Открываем окно управления расписаниями
        ScheduleManagementView(self)

    def open_flight_search(self):
        """Открытие окна поиска рейсов"""
        from app.views.flight_search_view import FlightSearchView
        FlightSearchView(self, self.user)

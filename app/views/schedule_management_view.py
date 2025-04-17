import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
from app.controllers.flight_controller import FlightController

class ScheduleManagementView(tk.Toplevel):
    """Окно управления расписанием рейсов"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.title("Manage Flight Schedules")
        self.geometry("1000x600")
        self.resizable(True, True)

        # Инициализация переменных
        self.selected_schedule = None

        # Создаем интерфейс
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Фрейм фильтров
        filter_frame = ttk.LabelFrame(self, text="Filter by")
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        # Фильтры по аэропортам
        airport_frame = ttk.Frame(filter_frame)
        airport_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(airport_frame, text="From").grid(row=0, column=0, padx=5, pady=5)
        self.from_var = tk.StringVar()
        self.from_combo = ttk.Combobox(airport_frame, textvariable=self.from_var, width=15)
        self.from_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(airport_frame, text="To").grid(row=0, column=2, padx=5, pady=5)
        self.to_var = tk.StringVar()
        self.to_combo = ttk.Combobox(airport_frame, textvariable=self.to_var, width=15)
        self.to_combo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(airport_frame, text="Sort by").grid(row=0, column=4, padx=5, pady=5)
        self.sort_by_var = tk.StringVar(value="Date-Time")
        self.sort_by_combo = ttk.Combobox(airport_frame, textvariable=self.sort_by_var, width=15)
        self.sort_by_combo['values'] = ["Date-Time", "Economy Price", "Confirmation Status"]
        self.sort_by_combo.grid(row=0, column=5, padx=5, pady=5)

        # Фильтры по дате и номеру рейса
        date_frame = ttk.Frame(filter_frame)
        date_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(date_frame, text="Outbound").grid(row=0, column=0, padx=5, pady=5)
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(date_frame, text="Flight Number").grid(row=0, column=2, padx=5, pady=5)
        self.flight_number_var = tk.StringVar()
        self.flight_number_entry = ttk.Entry(date_frame, textvariable=self.flight_number_var, width=15)
        self.flight_number_entry.grid(row=0, column=3, padx=5, pady=5)

        # Кнопка применения фильтров
        ttk.Button(date_frame, text="Apply", command=self.apply_filters).grid(row=0, column=4, padx=5, pady=5)

        # Таблица расписаний
        self.create_schedule_table()

        # Кнопки управления
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(button_frame, text="Cancel Flight", command=self.toggle_flight_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit Flight", command=self.edit_flight).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Import Changes", command=self.import_changes).pack(side=tk.RIGHT, padx=5)

    def create_schedule_table(self):
        # Фрейм для таблицы
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Создаем таблицу
        columns = ("Date", "Time", "From", "To", "Flight number", "Aircraft", "Economy price", "Business price", "First class price")
        self.schedule_tree = ttk.Treeview(table_frame, columns=columns, show='headings')

        # Настройка столбцов
        for col in columns:
            self.schedule_tree.heading(col, text=col)
            self.schedule_tree.column(col, width=100)

        # Добавляем скроллбары
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.schedule_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.schedule_tree.xview)
        self.schedule_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Размещаем элементы
        self.schedule_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        # Настраиваем растяжение
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Привязываем обработчик выбора
        self.schedule_tree.bind('<<TreeviewSelect>>', self.on_schedule_select)

    def load_data(self):
        """Загрузка данных для комбо-боксов"""
        # Загружаем аэропорты
        airports = FlightController.get_all_airports()

        # Добавляем аэропорты в комбо-боксы
        self.from_combo['values'] = [airport.iata_code for airport in airports]
        self.to_combo['values'] = [airport.iata_code for airport in airports]

        # Загружаем расписания
        self.load_schedules()

    def load_schedules(self, from_airport=None, to_airport=None, date=None, flight_number=None, sort_by="date_time"):
        """Загрузка расписаний с применением фильтров"""
        # Очищаем таблицу
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)

        # Получаем расписания
        schedules = FlightController.get_filtered_schedules(from_airport, to_airport, date, flight_number, sort_by)

        # Заполняем таблицу
        for schedule in schedules:
            # Получаем данные о маршруте и самолете
            from_code = schedule.route.departure_airport.iata_code
            to_code = schedule.route.arrival_airport.iata_code
            aircraft_name = schedule.aircraft.name

            # Форматируем дату и время
            date_str = schedule.date.strftime("%d/%m/%Y")
            time_str = schedule.time.strftime("%H:%M")

            # Рассчитываем цены для разных классов
            economy_price = schedule.economy_price
            business_price = schedule.business_price
            first_class_price = schedule.first_class_price

            # Добавляем строку в таблицу
            values = (
                date_str,
                time_str,
                from_code,
                to_code,
                schedule.flight_number,
                aircraft_name,
                f"${int(economy_price)}",
                f"${int(business_price)}",
                f"${int(first_class_price)}"
            )

            # Вставляем в таблицу с ID расписания в качестве идентификатора
            item_id = self.schedule_tree.insert('', tk.END, values=values, iid=str(schedule.id))

            # Если рейс отменен, выделяем его красным цветом
            if not schedule.confirmed:
                self.schedule_tree.item(item_id, tags=('cancelled',))

        # Настраиваем тег для отмененных рейсов
        self.schedule_tree.tag_configure('cancelled', background='#ffcccc')

    def apply_filters(self):
        """Применение фильтров к списку расписаний"""
        # Получаем значения фильтров
        from_code = self.from_var.get()
        to_code = self.to_var.get()
        date_str = self.date_var.get()
        flight_number = self.flight_number_var.get()
        sort_by_text = self.sort_by_var.get()

        # Преобразуем значение сортировки
        sort_by = "date_time"  # По умолчанию
        if sort_by_text == "Economy Price":
            sort_by = "economy_price"
        elif sort_by_text == "Confirmation Status":
            sort_by = "confirmed"

        # Получаем объекты аэропортов
        from_airport = None
        to_airport = None

        if from_code:
            airports = FlightController.get_all_airports()
            from_airport = next((a for a in airports if a.iata_code == from_code), None)

        if to_code:
            airports = FlightController.get_all_airports()
            to_airport = next((a for a in airports if a.iata_code == to_code), None)

        # Парсим дату, если указана
        date = None
        if date_str:
            try:
                day, month, year = map(int, date_str.split('/'))
                date = datetime.date(year, month, day)
            except:
                messagebox.showerror("Invalid Input", "Please enter date in format DD/MM/YYYY")
                return

        # Загружаем расписания с фильтрами
        self.load_schedules(from_airport, to_airport, date, flight_number, sort_by)

    def on_schedule_select(self, event):
        """Обработка выбора расписания в таблице"""
        selected_items = self.schedule_tree.selection()
        if selected_items:
            self.selected_schedule = selected_items[0]  # ID расписания

    def toggle_flight_status(self):
        """Изменение статуса рейса (подтвержден/отменен)"""
        if not self.selected_schedule:
            messagebox.showerror("No Selection", "Please select a flight to toggle status")
            return

        # Получаем ID расписания
        schedule_id = int(self.selected_schedule)

        # Изменяем статус
        success, message = FlightController.toggle_flight_status(schedule_id)

        if success:
            messagebox.showinfo("Success", message)
            # Обновляем список расписаний
            self.apply_filters()
        else:
            messagebox.showerror("Error", message)

    def edit_flight(self):
        """Редактирование выбранного рейса"""
        if not self.selected_schedule:
            messagebox.showerror("No Selection", "Please select a flight to edit")
            return

        # Получаем ID расписания
        schedule_id = int(self.selected_schedule)

        # Открываем окно редактирования
        EditScheduleDialog(self, schedule_id)

    def import_changes(self):
        """Импорт изменений расписания из файла"""
        # Открываем диалог выбора файла
        file_path = filedialog.askopenfilename(
            title="Select file with schedule changes",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            # Читаем содержимое файла
            with open(file_path, 'r') as file:
                file_content = file.read()

            # Импортируем изменения
            success, result = FlightController.import_schedule_changes(file_content)

            if success:
                # Показываем результаты
                message = f"Successful Changes Applied: {result['success']}\n"
                message += f"Duplicate Records Discarded: {result['duplicates']}\n"
                message += f"Records with missing fields discarded: {result['missing_fields']}"

                messagebox.showinfo("Import Results", message)

                # Обновляем список расписаний
                self.apply_filters()
            else:
                messagebox.showerror("Import Error", str(result))

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


class EditScheduleDialog(tk.Toplevel):
    """Диалог редактирования расписания"""

    def __init__(self, parent, schedule_id):
        super().__init__(parent)
        self.parent = parent
        self.schedule_id = schedule_id

        self.title("Schedule edit")
        self.geometry("500x250")
        self.resizable(False, False)
        self.transient(parent)  # Делаем окно модальным
        self.grab_set()  # Захватываем фокус

        # Загружаем данные расписания
        self.schedule = FlightController.get_flight_by_id(schedule_id)
        if not self.schedule:
            messagebox.showerror("Error", "Schedule not found")
            self.destroy()
            return

        # Создаем интерфейс
        self.create_widgets()

        # Ждем закрытия окна
        self.wait_window(self)

    def create_widgets(self):
        # Фрейм маршрута
        route_frame = ttk.LabelFrame(self, text="Flight route")
        route_frame.pack(fill=tk.X, padx=10, pady=10)

        # Информация о маршруте (только для чтения)
        from_code = self.schedule.route.departure_airport.iata_code
        to_code = self.schedule.route.arrival_airport.iata_code
        aircraft_name = self.schedule.aircraft.name

        ttk.Label(route_frame, text="From:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(route_frame, text=from_code).grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(route_frame, text="To:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        ttk.Label(route_frame, text=to_code).grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(route_frame, text="Aircraft:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        ttk.Label(route_frame, text=aircraft_name).grid(row=0, column=5, padx=5, pady=5, sticky='w')

        # Фрейм редактируемых данных
        edit_frame = ttk.Frame(self)
        edit_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Дата
        ttk.Label(edit_frame, text="Date:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.date_var = tk.StringVar(value=self.schedule.date.strftime("%d/%m/%Y"))
        self.date_entry = ttk.Entry(edit_frame, textvariable=self.date_var, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        # Время
        ttk.Label(edit_frame, text="Time:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.time_var = tk.StringVar(value=self.schedule.time.strftime("%H:%M"))
        self.time_entry = ttk.Entry(edit_frame, textvariable=self.time_var, width=15)
        self.time_entry.grid(row=0, column=3, padx=5, pady=5)

        # Цена эконом-класса
        ttk.Label(edit_frame, text="Economy price: $").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.price_var = tk.StringVar(value=str(int(self.schedule.economy_price)))
        self.price_entry = ttk.Entry(edit_frame, textvariable=self.price_var, width=15)
        self.price_entry.grid(row=1, column=1, padx=5, pady=5)

        # Кнопки
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Update", command=self.update_schedule).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def update_schedule(self):
        """Обновление данных расписания"""
        try:
            # Парсим дату
            date_str = self.date_var.get()
            day, month, year = map(int, date_str.split('/'))
            date = datetime.date(year, month, day)

            # Парсим время
            time_str = self.time_var.get()
            hour, minute = map(int, time_str.split(':'))
            time = datetime.time(hour, minute)

            # Парсим цену
            price = float(self.price_var.get())

            # Обновляем расписание
            success, message = FlightController.update_schedule(self.schedule_id, date, time, price)

            if success:
                messagebox.showinfo("Success", message)
                # Обновляем список расписаний в родительском окне
                self.parent.apply_filters()
                self.destroy()
            else:
                messagebox.showerror("Error", message)

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid date (DD/MM/YYYY), time (HH:MM) and price")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

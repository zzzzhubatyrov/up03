import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from app.controllers.flight_controller import FlightController

class FlightSearchView(tk.Toplevel):
    """Окно поиска рейсов"""

    def __init__(self, parent, user=None):
        super().__init__(parent)
        self.parent = parent
        self.user = user

        self.title("Search for flights")
        self.geometry("800x600")
        self.resizable(True, True)

        # Инициализация переменных
        self.selected_outbound_flight = None
        self.selected_return_flight = None
        self.passengers_count = 1

        # Создаем интерфейс
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Основной фрейм параметров поиска
        search_frame = ttk.LabelFrame(self, text="Search Parameters")
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        # Выбор аэропортов и типа кабины
        airport_frame = ttk.Frame(search_frame)
        airport_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(airport_frame, text="From").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.from_var = tk.StringVar()
        self.from_combo = ttk.Combobox(airport_frame, textvariable=self.from_var, width=15)
        self.from_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(airport_frame, text="To").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.to_var = tk.StringVar()
        self.to_combo = ttk.Combobox(airport_frame, textvariable=self.to_var, width=15)
        self.to_combo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(airport_frame, text="Cabin Type").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.cabin_type_var = tk.StringVar(value="Economy")
        self.cabin_type_combo = ttk.Combobox(airport_frame, textvariable=self.cabin_type_var, width=15)
        self.cabin_type_combo['values'] = ["Economy", "Business", "First Class"]
        self.cabin_type_combo.grid(row=0, column=5, padx=5, pady=5)

        # Тип поездки и даты
        trip_frame = ttk.Frame(search_frame)
        trip_frame.pack(fill=tk.X, padx=5, pady=5)

        # Тип поездки (в одну сторону или туда-обратно)
        self.trip_type_var = tk.StringVar(value="return")
        ttk.Radiobutton(trip_frame, text="Return", variable=self.trip_type_var, value="return").grid(row=0, column=0, padx=5, pady=5)
        ttk.Radiobutton(trip_frame, text="One way", variable=self.trip_type_var, value="oneway").grid(row=0, column=1, padx=5, pady=5)

        # Иконка для даты вылета
        outbound_icon_label = ttk.Label(trip_frame, text="↗")
        outbound_icon_label.grid(row=0, column=2, padx=2, pady=5, sticky='e')

        # Дата вылета
        ttk.Label(trip_frame, text="Outbound").grid(row=0, column=3, padx=2, pady=5, sticky='w')
        self.outbound_date_var = tk.StringVar()
        self.outbound_date_entry = ttk.Entry(trip_frame, textvariable=self.outbound_date_var, width=15)
        self.outbound_date_entry.grid(row=0, column=4, padx=5, pady=5)

        # Иконка для даты возвращения
        return_icon_label = ttk.Label(trip_frame, text="↙")
        return_icon_label.grid(row=0, column=5, padx=2, pady=5, sticky='e')

        # Дата возвращения
        ttk.Label(trip_frame, text="Return").grid(row=0, column=6, padx=2, pady=5, sticky='w')
        self.return_date_var = tk.StringVar()
        self.return_date_entry = ttk.Entry(trip_frame, textvariable=self.return_date_var, width=15)
        self.return_date_entry.grid(row=0, column=7, padx=5, pady=5)

        # Кнопка применения с иконкой поиска
        search_button = ttk.Button(trip_frame, text="🔍 Apply", command=self.search_flights)
        search_button.grid(row=0, column=8, padx=5, pady=5)

        # Фрейм рейсов вылета
        self.outbound_frame = ttk.LabelFrame(self, text="Outbound flight details")
        self.outbound_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Чекбокс для отображения +/- 3 дня для вылета
        self.outbound_extended_search_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.outbound_frame, text="Display three days before and after",
                        variable=self.outbound_extended_search_var,
                        command=self.search_flights).pack(anchor=tk.W, padx=5, pady=5)

        # Таблица рейсов вылета
        columns = ("From", "To", "Date", "Time", "Flight Number(s)", "Cabin Price", "Number of stops")
        self.outbound_tree = ttk.Treeview(self.outbound_frame, columns=columns, show='headings', height=6)

        # Настройка столбцов
        for col in columns:
            self.outbound_tree.heading(col, text=col)
            if col == "Flight Number(s)":
                self.outbound_tree.column(col, width=150)
            elif col == "Cabin Price":
                self.outbound_tree.column(col, width=100, anchor=tk.CENTER)
            elif col == "Number of stops":
                self.outbound_tree.column(col, width=100, anchor=tk.CENTER)
            else:
                self.outbound_tree.column(col, width=100)

        # Добавляем скроллбары
        outbound_vsb = ttk.Scrollbar(self.outbound_frame, orient="vertical", command=self.outbound_tree.yview)
        outbound_hsb = ttk.Scrollbar(self.outbound_frame, orient="horizontal", command=self.outbound_tree.xview)
        self.outbound_tree.configure(yscrollcommand=outbound_vsb.set, xscrollcommand=outbound_hsb.set)

        # Размещаем элементы
        self.outbound_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        outbound_vsb.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.outbound_tree.bind('<<TreeviewSelect>>', self.on_outbound_select)

        # Фрейм рейсов возвращения (изначально скрыт)
        self.return_frame = ttk.LabelFrame(self, text="Return flight details")

        # Чекбокс для отображения +/- 3 дня для возвращения
        self.return_extended_search_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.return_frame, text="Display three days before and after",
                        variable=self.return_extended_search_var,
                        command=self.search_flights).pack(anchor=tk.W, padx=5, pady=5)

        # Таблица рейсов возвращения
        self.return_tree = ttk.Treeview(self.return_frame, columns=columns, show='headings', height=6)

        # Настройка столбцов
        for col in columns:
            self.return_tree.heading(col, text=col)
            if col == "Flight Number(s)":
                self.return_tree.column(col, width=150)
            elif col == "Cabin Price":
                self.return_tree.column(col, width=100, anchor=tk.CENTER)
            elif col == "Number of stops":
                self.return_tree.column(col, width=100, anchor=tk.CENTER)
            else:
                self.return_tree.column(col, width=100)

        # Добавляем скроллбары
        return_vsb = ttk.Scrollbar(self.return_frame, orient="vertical", command=self.return_tree.yview)
        return_hsb = ttk.Scrollbar(self.return_frame, orient="horizontal", command=self.return_tree.xview)
        self.return_tree.configure(yscrollcommand=return_vsb.set, xscrollcommand=return_hsb.set)

        # Размещаем элементы
        self.return_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        return_vsb.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.return_tree.bind('<<TreeviewSelect>>', self.on_return_select)

        # Фрейм бронирования
        booking_frame = ttk.LabelFrame(self, text="Confirm booking for")
        booking_frame.pack(fill=tk.X, padx=10, pady=10)

        # Количество пассажиров
        booking_inner_frame = ttk.Frame(booking_frame)
        booking_inner_frame.pack(fill=tk.X, padx=5, pady=5)

        self.passengers_var = tk.StringVar(value="1")
        passengers_entry = ttk.Entry(booking_inner_frame, textvariable=self.passengers_var, width=5)
        passengers_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(booking_inner_frame, text="Passengers").pack(side=tk.LEFT, padx=5)

        # Кнопки
        button_frame = ttk.Frame(booking_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="Book Flight", command=self.book_flight).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def load_data(self):
        """Загрузка данных для комбо-боксов"""
        # Загружаем аэропорты
        airports = FlightController.get_all_airports()

        # Добавляем аэропорты в комбо-боксы
        self.from_combo['values'] = [airport.iata_code for airport in airports]
        self.to_combo['values'] = [airport.iata_code for airport in airports]

        # Устанавливаем даты по умолчанию (сегодня и завтра)
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)

        self.outbound_date_var.set(today.strftime("%d/%m/%Y"))
        self.return_date_var.set(tomorrow.strftime("%d/%m/%Y"))

    def search_flights(self):
        """Поиск рейсов по заданным параметрам"""
        # Очищаем предыдущие результаты
        for item in self.outbound_tree.get_children():
            self.outbound_tree.delete(item)

        if hasattr(self, 'return_tree'):
            for item in self.return_tree.get_children():
                self.return_tree.delete(item)

        # Получаем параметры поиска
        from_airport_code = self.from_var.get()
        to_airport_code = self.to_var.get()
        cabin_type = self.cabin_type_var.get()
        trip_type = self.trip_type_var.get()

        # Проверяем входные данные
        if not from_airport_code or not to_airport_code:
            messagebox.showerror("Invalid Input", "Please select departure and arrival airports")
            return

        if from_airport_code == to_airport_code:
            messagebox.showerror("Invalid Input", "Departure and arrival airports cannot be the same")
            return

        # Парсим даты
        try:
            outbound_date_str = self.outbound_date_var.get()
            day, month, year = map(int, outbound_date_str.split('/'))
            outbound_date = datetime.date(year, month, day)
        except:
            messagebox.showerror("Invalid Input", "Please enter outbound date in format DD/MM/YYYY")
            return

        # Ищем рейсы вылета
        self.search_outbound_flights(from_airport_code, to_airport_code, outbound_date, cabin_type)

        # Если это поездка туда-обратно, ищем рейсы возвращения
        if trip_type == "return":
            try:
                return_date_str = self.return_date_var.get()
                day, month, year = map(int, return_date_str.split('/'))
                return_date = datetime.date(year, month, day)

                if return_date < outbound_date:
                    messagebox.showerror("Invalid Input", "Return date cannot be before outbound date")
                    return

                # Показываем фрейм рейсов возвращения
                self.return_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

                # Ищем рейсы возвращения
                self.search_return_flights(to_airport_code, from_airport_code, return_date, cabin_type)
            except:
                messagebox.showerror("Invalid Input", "Please enter return date in format DD/MM/YYYY")
                return
        else:
            # Скрываем фрейм рейсов возвращения для поездок в одну сторону
            self.return_frame.pack_forget()

    def search_outbound_flights(self, from_airport_code, to_airport_code, date, cabin_type):
        """Поиск рейсов вылета"""
        # Ищем рейсы через контроллер
        flights = FlightController.search_flights(
            from_airport_code,
            to_airport_code,
            date,
            self.outbound_extended_search_var.get()
        )

        # Добавляем прямые рейсы в таблицу
        for flight in flights['direct']:
            price = flight.get_price_by_cabin_type(cabin_type)

            values = (
                from_airport_code,
                to_airport_code,
                flight.date.strftime("%d/%m/%Y"),
                flight.time.strftime("%H:%M"),
                flight.flight_number,
                f"${int(price)}",
                "0"  # Прямой рейс имеет 0 пересадок
            )

            # Вставляем в таблицу с ID рейса в качестве идентификатора
            self.outbound_tree.insert('', tk.END, values=values, iid=f"direct_{flight.id}")

        # Добавляем рейсы с пересадкой в таблицу
        for i, (first_leg, second_leg) in enumerate(flights['connecting']):
            # Рассчитываем общую цену
            first_leg_price = first_leg.get_price_by_cabin_type(cabin_type)
            second_leg_price = second_leg.get_price_by_cabin_type(cabin_type)
            total_price = first_leg_price + second_leg_price

            values = (
                from_airport_code,
                to_airport_code,
                first_leg.date.strftime("%d/%m/%Y"),
                first_leg.time.strftime("%H:%M"),
                f"{first_leg.flight_number} - {second_leg.flight_number}",
                f"${int(total_price)}",
                "1"  # Одна пересадка
            )

            # Вставляем в таблицу с уникальным ID
            self.outbound_tree.insert('', tk.END, values=values, iid=f"connecting_{i}_{first_leg.id}_{second_leg.id}")

    def search_return_flights(self, from_airport_code, to_airport_code, date, cabin_type):
        """Поиск рейсов возвращения"""
        # Аналогично search_outbound_flights, но для рейсов возвращения
        flights = FlightController.search_flights(
            from_airport_code,
            to_airport_code,
            date,
            self.return_extended_search_var.get()
        )

        # Добавляем прямые рейсы в таблицу
        for flight in flights['direct']:
            price = flight.get_price_by_cabin_type(cabin_type)

            values = (
                from_airport_code,
                to_airport_code,
                flight.date.strftime("%d/%m/%Y"),
                flight.time.strftime("%H:%M"),
                flight.flight_number,
                f"${int(price)}",
                "0"  # Прямой рейс имеет 0 пересадок
            )

            # Вставляем в таблицу с ID рейса в качестве идентификатора
            self.return_tree.insert('', tk.END, values=values, iid=f"direct_{flight.id}")

        # Добавляем рейсы с пересадкой в таблицу
        for i, (first_leg, second_leg) in enumerate(flights['connecting']):
            # Рассчитываем общую цену
            first_leg_price = first_leg.get_price_by_cabin_type(cabin_type)
            second_leg_price = second_leg.get_price_by_cabin_type(cabin_type)
            total_price = first_leg_price + second_leg_price

            values = (
                from_airport_code,
                to_airport_code,
                first_leg.date.strftime("%d/%m/%Y"),
                first_leg.time.strftime("%H:%M"),
                f"{first_leg.flight_number} - {second_leg.flight_number}",
                f"${int(total_price)}",
                "1"  # Одна пересадка
            )

            # Вставляем в таблицу с уникальным ID
            self.return_tree.insert('', tk.END, values=values, iid=f"connecting_{i}_{first_leg.id}_{second_leg.id}")

    def on_outbound_select(self, event):
        """Обработка выбора рейса вылета"""
        # Получаем выбранный элемент
        selected_id = self.outbound_tree.selection()
        if selected_id:
            self.selected_outbound_flight = selected_id[0]

    def on_return_select(self, event):
        """Обработка выбора рейса возвращения"""
        # Получаем выбранный элемент
        selected_id = self.return_tree.selection()
        if selected_id:
            self.selected_return_flight = selected_id[0]

    def book_flight(self):
        """Бронирование выбранных рейсов"""
        # Проверяем выбор
        if not self.selected_outbound_flight:
            messagebox.showerror("No Selection", "Please select an outbound flight")
            return

        if self.trip_type_var.get() == "return" and not self.selected_return_flight:
            messagebox.showerror("No Selection", "Please select a return flight")
            return

        # Получаем количество пассажиров
        try:
            self.passengers_count = int(self.passengers_var.get())
            if self.passengers_count <= 0:
                raise ValueError("Passenger count must be positive")
        except:
            messagebox.showerror("Invalid Input", "Please enter a valid number of passengers")
            return

        # Проверяем наличие мест
        if not self.check_seat_availability():
            messagebox.showerror("No Seats Available", "Not enough seats available for the selected flights")
            return

        # Открываем окно подтверждения бронирования
        from app.views.booking_confirmation_view import BookingConfirmationView

        # Определяем, есть ли обратный рейс
        return_flight = None
        if self.trip_type_var.get() == "return" and self.selected_return_flight:
            return_flight = self.selected_return_flight

        # Открываем окно подтверждения бронирования
        BookingConfirmationView(
            self,
            self.selected_outbound_flight,
            return_flight,
            self.cabin_type_var.get(),
            self.user
        )

    def check_seat_availability(self):
        """Проверка наличия свободных мест"""
        cabin_type = self.cabin_type_var.get()

        # Проверяем рейс вылета
        if self.selected_outbound_flight.startswith("direct_"):
            # Прямой рейс
            flight_id = int(self.selected_outbound_flight.split("_")[1])
            if not FlightController.check_seat_availability(flight_id, cabin_type, self.passengers_count):
                return False

        # Для рейсов с пересадкой нужно проверить оба сегмента
        # Это упрощенная версия

        # Проверяем рейс возвращения, если применимо
        if self.trip_type_var.get() == "return" and self.selected_return_flight:
            if self.selected_return_flight.startswith("direct_"):
                # Прямой рейс
                flight_id = int(self.selected_return_flight.split("_")[1])
                if not FlightController.check_seat_availability(flight_id, cabin_type, self.passengers_count):
                    return False

        return True



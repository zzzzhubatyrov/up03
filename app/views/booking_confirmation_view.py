import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from app.controllers.flight_controller import FlightController

class BookingConfirmationView(tk.Toplevel):
    """Окно подтверждения бронирования"""
    
    def __init__(self, parent, outbound_flight, return_flight=None, cabin_type="Economy", user=None):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        
        # Сохраняем информацию о рейсах
        self.outbound_flight = outbound_flight
        self.return_flight = return_flight
        self.cabin_type = cabin_type
        
        # Список пассажиров
        self.passengers = []
        
        # Настройка окна
        self.title("Booking confirmation")
        self.geometry("700x600")
        self.resizable(True, True)
        
        # Создаем интерфейс
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Фрейм для информации о рейсе туда
        outbound_frame = ttk.LabelFrame(main_frame, text="Outbound flight details")
        outbound_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Информация о рейсе туда
        outbound_info_frame = ttk.Frame(outbound_frame)
        outbound_info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(outbound_info_frame, text="From:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.outbound_from_label = ttk.Label(outbound_info_frame, text="")
        self.outbound_from_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(outbound_info_frame, text="To:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.outbound_to_label = ttk.Label(outbound_info_frame, text="")
        self.outbound_to_label.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        
        ttk.Label(outbound_info_frame, text="Cabin Type:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.outbound_cabin_label = ttk.Label(outbound_info_frame, text="")
        self.outbound_cabin_label.grid(row=0, column=5, padx=5, pady=5, sticky='w')
        
        ttk.Label(outbound_info_frame, text="Date:").grid(row=0, column=6, padx=5, pady=5, sticky='w')
        self.outbound_date_label = ttk.Label(outbound_info_frame, text="")
        self.outbound_date_label.grid(row=0, column=7, padx=5, pady=5, sticky='w')
        
        ttk.Label(outbound_info_frame, text="Flight number:").grid(row=0, column=8, padx=5, pady=5, sticky='w')
        self.outbound_flight_number_label = ttk.Label(outbound_info_frame, text="")
        self.outbound_flight_number_label.grid(row=0, column=9, padx=5, pady=5, sticky='w')
        
        # Фрейм для информации о рейсе обратно (если есть)
        self.return_frame = ttk.LabelFrame(main_frame, text="Return flight details")
        if self.return_flight:
            self.return_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Информация о рейсе обратно
            return_info_frame = ttk.Frame(self.return_frame)
            return_info_frame.pack(fill=tk.X, padx=5, pady=5)
            
            ttk.Label(return_info_frame, text="From:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
            self.return_from_label = ttk.Label(return_info_frame, text="")
            self.return_from_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')
            
            ttk.Label(return_info_frame, text="To:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
            self.return_to_label = ttk.Label(return_info_frame, text="")
            self.return_to_label.grid(row=0, column=3, padx=5, pady=5, sticky='w')
            
            ttk.Label(return_info_frame, text="Cabin Type:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
            self.return_cabin_label = ttk.Label(return_info_frame, text="")
            self.return_cabin_label.grid(row=0, column=5, padx=5, pady=5, sticky='w')
            
            ttk.Label(return_info_frame, text="Date:").grid(row=0, column=6, padx=5, pady=5, sticky='w')
            self.return_date_label = ttk.Label(return_info_frame, text="")
            self.return_date_label.grid(row=0, column=7, padx=5, pady=5, sticky='w')
            
            ttk.Label(return_info_frame, text="Flight number:").grid(row=0, column=8, padx=5, pady=5, sticky='w')
            self.return_flight_number_label = ttk.Label(return_info_frame, text="")
            self.return_flight_number_label.grid(row=0, column=9, padx=5, pady=5, sticky='w')
        
        # Фрейм для ввода данных пассажира
        passenger_frame = ttk.LabelFrame(main_frame, text="Passenger details")
        passenger_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Форма ввода данных пассажира
        form_frame = ttk.Frame(passenger_frame)
        form_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Имя
        ttk.Label(form_frame, text="Firstname").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.firstname_var = tk.StringVar()
        self.firstname_entry = ttk.Entry(form_frame, textvariable=self.firstname_var, width=20)
        self.firstname_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        # Фамилия
        ttk.Label(form_frame, text="Lastname").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.lastname_var = tk.StringVar()
        self.lastname_entry = ttk.Entry(form_frame, textvariable=self.lastname_var, width=20)
        self.lastname_entry.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        
        # Дата рождения
        ttk.Label(form_frame, text="Birthdate").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.birthdate_var = tk.StringVar()
        self.birthdate_entry = ttk.Entry(form_frame, textvariable=self.birthdate_var, width=20)
        self.birthdate_entry.grid(row=0, column=5, padx=5, pady=5, sticky='w')
        ttk.Label(form_frame, text="(dd / mm / yyyy)").grid(row=0, column=6, padx=5, pady=5, sticky='w')
        
        # Номер паспорта
        ttk.Label(form_frame, text="Passport number").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.passport_number_var = tk.StringVar()
        self.passport_number_entry = ttk.Entry(form_frame, textvariable=self.passport_number_var, width=20)
        self.passport_number_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        # Страна паспорта
        ttk.Label(form_frame, text="Passport country").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.passport_country_var = tk.StringVar()
        self.passport_country_combo = ttk.Combobox(form_frame, textvariable=self.passport_country_var, width=20)
        self.passport_country_combo.grid(row=1, column=3, padx=5, pady=5, sticky='w')
        
        # Телефон
        ttk.Label(form_frame, text="Phone").grid(row=1, column=4, padx=5, pady=5, sticky='w')
        self.phone_var = tk.StringVar()
        self.phone_entry = ttk.Entry(form_frame, textvariable=self.phone_var, width=20)
        self.phone_entry.grid(row=1, column=5, padx=5, pady=5, sticky='w')
        
        # Кнопка добавления пассажира
        add_button = ttk.Button(form_frame, text="Add passenger", command=self.add_passenger)
        add_button.grid(row=1, column=6, padx=5, pady=5, sticky='e')
        
        # Фрейм для списка пассажиров
        passengers_list_frame = ttk.LabelFrame(main_frame, text="Passengers list")
        passengers_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Таблица пассажиров
        columns = ("Firstname", "Lastname", "Birthdate", "Passport number", "Passport Country", "Phone")
        self.passengers_tree = ttk.Treeview(passengers_list_frame, columns=columns, show='headings', height=10)
        
        # Настройка столбцов
        for col in columns:
            self.passengers_tree.heading(col, text=col)
            self.passengers_tree.column(col, width=100)
        
        # Добавляем скроллбары
        passengers_vsb = ttk.Scrollbar(passengers_list_frame, orient="vertical", command=self.passengers_tree.yview)
        passengers_hsb = ttk.Scrollbar(passengers_list_frame, orient="horizontal", command=self.passengers_tree.xview)
        self.passengers_tree.configure(yscrollcommand=passengers_vsb.set, xscrollcommand=passengers_hsb.set)
        
        # Размещаем элементы
        self.passengers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        passengers_vsb.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Кнопка удаления пассажира
        remove_button = ttk.Button(passengers_list_frame, text="Remove passenger", command=self.remove_passenger)
        remove_button.pack(side=tk.BOTTOM, padx=5, pady=5, anchor='e')
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Кнопка возврата к поиску
        back_button = ttk.Button(button_frame, text="Back to search for flights", command=self.back_to_search)
        back_button.pack(side=tk.LEFT, padx=5)
        
        # Кнопка подтверждения бронирования
        confirm_button = ttk.Button(button_frame, text="Confirm booking", command=self.confirm_booking)
        confirm_button.pack(side=tk.RIGHT, padx=5)
    
    def load_data(self):
        """Загрузка данных"""
        # Загружаем информацию о рейсе туда
        if isinstance(self.outbound_flight, str) and self.outbound_flight.startswith("direct_"):
            # Прямой рейс
            flight_id = int(self.outbound_flight.split("_")[1])
            flight = FlightController.get_flight_by_id(flight_id)
            
            if flight:
                self.outbound_from_label.config(text=flight.route.departure_airport.iata_code)
                self.outbound_to_label.config(text=flight.route.arrival_airport.iata_code)
                self.outbound_cabin_label.config(text=self.cabin_type)
                self.outbound_date_label.config(text=flight.date.strftime("%d/%m/%Y"))
                self.outbound_flight_number_label.config(text=flight.flight_number)
        
        # Загружаем информацию о рейсе обратно (если есть)
        if self.return_flight and isinstance(self.return_flight, str) and self.return_flight.startswith("direct_"):
            # Прямой рейс
            flight_id = int(self.return_flight.split("_")[1])
            flight = FlightController.get_flight_by_id(flight_id)
            
            if flight:
                self.return_from_label.config(text=flight.route.departure_airport.iata_code)
                self.return_to_label.config(text=flight.route.arrival_airport.iata_code)
                self.return_cabin_label.config(text=self.cabin_type)
                self.return_date_label.config(text=flight.date.strftime("%d/%m/%Y"))
                self.return_flight_number_label.config(text=flight.flight_number)
        
        # Загружаем список стран для выпадающего списка
        countries = FlightController.get_all_countries()
        self.passport_country_combo['values'] = [country.name for country in countries]
    
    def add_passenger(self):
        """Добавление пассажира в список"""
        # Проверяем, что все обязательные поля заполнены
        if not self.validate_passenger_data():
            return
        
        # Получаем данные пассажира
        firstname = self.firstname_var.get()
        lastname = self.lastname_var.get()
        birthdate = self.birthdate_var.get()
        passport_number = self.passport_number_var.get()
        passport_country = self.passport_country_var.get()
        phone = self.phone_var.get()
        
        # Добавляем пассажира в список
        self.passengers.append({
            'firstname': firstname,
            'lastname': lastname,
            'birthdate': birthdate,
            'passport_number': passport_number,
            'passport_country': passport_country,
            'phone': phone
        })
        
        # Добавляем пассажира в таблицу
        self.passengers_tree.insert('', tk.END, values=(
            firstname,
            lastname,
            birthdate,
            passport_number,
            passport_country,
            phone
        ))
        
        # Очищаем поля ввода
        self.clear_passenger_form()
    
    def remove_passenger(self):
        """Удаление пассажира из списка"""
        # Получаем выбранного пассажира
        selected_items = self.passengers_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a passenger to remove")
            return
        
        # Удаляем пассажира из таблицы и списка
        for item in selected_items:
            index = self.passengers_tree.index(item)
            self.passengers_tree.delete(item)
            if 0 <= index < len(self.passengers):
                self.passengers.pop(index)
    
    def validate_passenger_data(self):
        """Проверка данных пассажира"""
        # Проверяем, что все обязательные поля заполнены
        if not self.firstname_var.get():
            messagebox.showerror("Error", "Please enter passenger's firstname")
            return False
        
        if not self.lastname_var.get():
            messagebox.showerror("Error", "Please enter passenger's lastname")
            return False
        
        if not self.birthdate_var.get():
            messagebox.showerror("Error", "Please enter passenger's birthdate")
            return False
        
        # Проверяем формат даты рождения
        try:
            day, month, year = map(int, self.birthdate_var.get().split('/'))
            birthdate = datetime.date(year, month, day)
        except:
            messagebox.showerror("Error", "Please enter birthdate in format DD/MM/YYYY")
            return False
        
        if not self.passport_number_var.get():
            messagebox.showerror("Error", "Please enter passenger's passport number")
            return False
        
        if not self.passport_country_var.get():
            messagebox.showerror("Error", "Please select passenger's passport country")
            return False
        
        if not self.phone_var.get():
            messagebox.showerror("Error", "Please enter passenger's phone number")
            return False
        
        return True
    
    def clear_passenger_form(self):
        """Очистка формы ввода данных пассажира"""
        self.firstname_var.set("")
        self.lastname_var.set("")
        self.birthdate_var.set("")
        self.passport_number_var.set("")
        self.passport_country_var.set("")
        self.phone_var.set("")
    
    def back_to_search(self):
        """Возврат к поиску рейсов"""
        self.destroy()
    
    def confirm_booking(self):
        """Подтверждение бронирования"""
        # Проверяем, что есть хотя бы один пассажир
        if not self.passengers:
            messagebox.showerror("Error", "Please add at least one passenger")
            return
        
        # Получаем ID пользователя, если он авторизован
        user_id = self.user.id if self.user else None
        
        # Получаем ID страны для каждого пассажира
        countries = FlightController.get_all_countries()
        country_dict = {country.name: country.id for country in countries}
        
        # Подготавливаем данные пассажиров
        passengers_data = []
        for passenger in self.passengers:
            # Преобразуем дату рождения в объект datetime
            day, month, year = map(int, passenger['birthdate'].split('/'))
            birthdate = datetime.date(year, month, day)
            
            # Получаем ID страны
            passport_country_id = country_dict.get(passenger['passport_country'])
            if not passport_country_id:
                messagebox.showerror("Error", f"Country not found: {passenger['passport_country']}")
                return
            
            # Добавляем данные пассажира
            passengers_data.append({
                'firstname': passenger['firstname'],
                'lastname': passenger['lastname'],
                'birthdate': birthdate,
                'passport_number': passenger['passport_number'],
                'passport_country_id': passport_country_id,
                'phone': passenger['phone'],
                'email': ''  # Можно добавить поле для email в форму
            })
        
        # Бронируем рейс туда
        if isinstance(self.outbound_flight, str) and self.outbound_flight.startswith("direct_"):
            # Прямой рейс
            flight_id = int(self.outbound_flight.split("_")[1])
            success, message = FlightController.book_flight(flight_id, self.cabin_type, passengers_data, user_id)
            
            if not success:
                messagebox.showerror("Error", message)
                return
        
        # Бронируем рейс обратно (если есть)
        if self.return_flight and isinstance(self.return_flight, str) and self.return_flight.startswith("direct_"):
            # Прямой рейс
            flight_id = int(self.return_flight.split("_")[1])
            success, message = FlightController.book_flight(flight_id, self.cabin_type, passengers_data, user_id)
            
            if not success:
                messagebox.showerror("Error", message)
                return
        
        # Показываем сообщение об успешном бронировании
        messagebox.showinfo("Success", "Booking confirmed successfully!")
        
        # Закрываем окно
        self.destroy()

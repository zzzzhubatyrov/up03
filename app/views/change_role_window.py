import tkinter as tk
from tkinter import ttk, messagebox
from app.controllers.user_controller import UserController
from app.models import Role

class ChangeRoleWindow(tk.Toplevel):
    """Окно изменения роли пользователя"""

    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.parent = parent
        self.user_id = user_id

        self.title("Change Role")
        self.geometry("400x250")
        self.resizable(False, False)
        self.transient(parent)  # Делаем окно модальным
        self.grab_set()  # Захватываем фокус

        # Получаем информацию о пользователе
        self.user = UserController.get_user_by_id(self.user_id)
        if not self.user:
            messagebox.showerror("Error", "User not found")
            self.destroy()
            return

        # Получаем список ролей
        self.roles = UserController.get_all_roles()

        # Создаем интерфейс
        self.create_widgets()

        # Ждем закрытия окна
        self.wait_window(self)

    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Информация о пользователе
        user_info_frame = ttk.LabelFrame(main_frame, text="User Information")
        user_info_frame.pack(fill=tk.X, padx=5, pady=5)

        # Имя пользователя
        ttk.Label(user_info_frame, text=f"Name: {self.user.firstname} {self.user.lastname}").pack(anchor=tk.W, padx=5, pady=2)

        # Email пользователя
        ttk.Label(user_info_frame, text=f"Email: {self.user.email}").pack(anchor=tk.W, padx=5, pady=2)

        # Текущая роль
        current_role = self.user.role.title if self.user.role else "None"
        ttk.Label(user_info_frame, text=f"Current Role: {current_role}").pack(anchor=tk.W, padx=5, pady=2)

        # Фрейм выбора новой роли
        role_frame = ttk.LabelFrame(main_frame, text="Select New Role")
        role_frame.pack(fill=tk.X, padx=5, pady=10)

        # Выбор роли
        self.role_var = tk.StringVar()

        # Создаем радиокнопки для каждой роли, кроме администратора
        for role in self.roles:
            if role.title.lower() != "administrator":  # Не позволяем назначать роль администратора
                ttk.Radiobutton(
                    role_frame,
                    text=role.title.capitalize(),
                    variable=self.role_var,
                    value=str(role.id)
                ).pack(anchor=tk.W, padx=5, pady=2)

        # Если у пользователя уже есть роль, выбираем ее
        if self.user.role:
            self.role_var.set(str(self.user.role.id))

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Save", command=self.save_role).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def save_role(self):
        """Сохранение новой роли пользователя"""
        # Проверяем, выбрана ли роль
        if not self.role_var.get():
            messagebox.showerror("Error", "Please select a role")
            return

        # Получаем ID выбранной роли
        role_id = int(self.role_var.get())

        # Если роль не изменилась, просто закрываем окно
        if self.user.role and self.user.role.id == role_id:
            self.destroy()
            return

        # Изменяем роль пользователя
        success, message = UserController.change_user_role(self.user_id, role_id)

        if success:
            messagebox.showinfo("Success", message)
            self.destroy()
        else:
            messagebox.showerror("Error", message)

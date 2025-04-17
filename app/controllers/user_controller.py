import datetime
from app.models import User, Role, Office, LoginAttempt, UserSession
from app.config.database import get_session

class UserController:
    """Контроллер для работы с пользователями"""

    @staticmethod
    def authenticate(email, password):
        """Аутентификация пользователя"""
        session = get_session()
        user = session.query(User).filter_by(email=email).first()

        if user and user.password == password:
            if not user.active:
                return None, "Ваша учетная запись отключена администратором"

            # Записываем успешную попытку входа
            login_attempt = LoginAttempt(
                user_id=user.id,
                timestamp=datetime.datetime.now(),
                success=True
            )
            session.add(login_attempt)

            # Создаем новый сеанс пользователя
            user_session = UserSession(
                user_id=user.id,
                login_time=datetime.datetime.now()
            )
            session.add(user_session)
            session.commit()

            # Загружаем все необходимые связанные объекты
            # чтобы избежать ошибки DetachedInstanceError
            role = user.role
            office = user.office

            # Создаем новую сессию для дальнейшей работы
            new_session = get_session()
            # Загружаем пользователя в новую сессию
            user_with_session = new_session.query(User).get(user.id)
            user_session_with_session = new_session.query(UserSession).get(user_session.id)

            return user_with_session, user_session_with_session
        else:
            # Записываем неудачную попытку входа
            if user:
                login_attempt = LoginAttempt(
                    user_id=user.id,
                    timestamp=datetime.datetime.now(),
                    success=False,
                    error_message="Неверный пароль"
                )
                session.add(login_attempt)
                session.commit()

            return None, "Неверный email или пароль"

    @staticmethod
    def get_all_users(office_filter=None):
        """Получение списка всех пользователей с возможностью фильтрации по офису"""
        session = get_session()
        query = session.query(User)

        if office_filter and office_filter != "All offices":
            query = query.join(Office).filter(Office.title == office_filter)

        return query.all()

    @staticmethod
    def add_user(email, firstname, lastname, office_title, password, birthdate=None, role_title="user"):
        """Добавление нового пользователя"""
        session = get_session()

        # Проверяем, что пользователя с таким email еще нет
        existing_user = session.query(User).filter_by(email=email).first()
        if existing_user:
            return False, "User with this email already exists"

        # Получаем офис по названию
        office = session.query(Office).filter_by(title=office_title).first()
        if not office:
            return False, f"Office '{office_title}' not found"

        # Получаем роль по названию
        role = session.query(Role).filter_by(title=role_title).first()
        if not role:
            return False, f"Role '{role_title}' not found"

        # Создаем нового пользователя
        user = User(
            office_id=office.id,
            role_id=role.id,
            email=email,
            password=password,
            firstname=firstname,
            lastname=lastname,
            birthdate=birthdate,
            active=True
        )

        try:
            session.add(user)
            session.commit()
            return True, "User added successfully"
        except Exception as e:
            session.rollback()
            return False, f"Error adding user: {str(e)}"

    @staticmethod
    def change_role(user_id, new_role_id):
        """Изменение роли пользователя"""
        session = get_session()
        user = session.query(User).get(user_id)

        if not user:
            return False, "Пользователь не найден"

        try:
            user.role_id = new_role_id
            session.commit()
            return True, "Роль пользователя успешно изменена"
        except Exception as e:
            session.rollback()
            return False, f"Ошибка при изменении роли: {str(e)}"

    @staticmethod
    def toggle_active(user_id):
        """Включение/отключение учетной записи пользователя"""
        session = get_session()
        user = session.query(User).get(user_id)

        if not user:
            return False, "Пользователь не найден"

        try:
            user.active = not user.active
            session.commit()
            status = "включена" if user.active else "отключена"
            return True, f"Учетная запись пользователя {status}"
        except Exception as e:
            session.rollback()
            return False, f"Ошибка при изменении статуса: {str(e)}"

    @staticmethod
    def close_session(user_session):
        """Закрытие сеанса пользователя"""
        session = get_session()

        try:
            user_session.logout_time = datetime.datetime.now()
            session.add(user_session)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return False

    @staticmethod
    def get_all_offices():
        """Получение списка всех офисов"""
        session = get_session()
        return session.query(Office).all()

    @staticmethod
    def get_user_by_id(user_id):
        """Получение пользователя по ID"""
        session = get_session()
        return session.query(User).get(user_id)

    @staticmethod
    def get_all_roles():
        """Получение списка всех ролей"""
        session = get_session()
        return session.query(Role).all()

    @staticmethod
    def change_user_role(user_id, role_id):
        """Изменение роли пользователя"""
        session = get_session()
        user = session.query(User).get(user_id)

        if not user:
            return False, "User not found"

        # Проверяем, что роль существует
        role = session.query(Role).get(role_id)
        if not role:
            return False, "Role not found"

        try:
            user.role_id = role_id
            session.commit()
            return True, f"Role successfully changed to {role.title}"
        except Exception as e:
            session.rollback()
            return False, f"Error changing role: {str(e)}"

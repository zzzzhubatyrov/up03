from app.config.database import get_session
from app.models import User, Office, Role, Country
import datetime

def add_users():
    """Добавление пользователей в офисы"""
    session = get_session()
    
    # Получаем роли
    user_role = session.query(Role).filter_by(title="user").first()
    admin_role = session.query(Role).filter_by(title="administrator").first()
    
    if not user_role or not admin_role:
        print("Роли не найдены. Создаем роли...")
        if not user_role:
            user_role = Role(title="user")
            session.add(user_role)
        if not admin_role:
            admin_role = Role(title="administrator")
            session.add(admin_role)
        session.commit()
    
    # Получаем офисы
    offices = session.query(Office).all()
    office_dict = {office.title: office for office in offices}
    
    # Проверяем, существуют ли уже пользователи
    existing_users = session.query(User).all()
    existing_emails = [user.email for user in existing_users]
    
    # Список пользователей для добавления
    users_to_add = [
        # Abu Dhabi - активные пользователи (зеленые)
        {
            "office": "Abu Dhabi",
            "role": user_role,
            "email": "ahmed@amonic.com",
            "password": "password",
            "firstname": "Ahmed",
            "lastname": "Al Mansouri",
            "birthdate": datetime.datetime(1985, 5, 15),
            "active": True
        },
        {
            "office": "Abu Dhabi",
            "role": user_role,
            "email": "fatima@amonic.com",
            "password": "password",
            "firstname": "Fatima",
            "lastname": "Al Zaabi",
            "birthdate": datetime.datetime(1990, 8, 23),
            "active": True
        },
        # Bahrain - активный пользователь (зеленый)
        {
            "office": "Bahrain",
            "role": user_role,
            "email": "mohammed@amonic.com",
            "password": "password",
            "firstname": "Mohammed",
            "lastname": "Al Khalifa",
            "birthdate": datetime.datetime(1982, 3, 10),
            "active": True
        },
        # Doha - активный пользователь (зеленый)
        {
            "office": "Doha",
            "role": user_role,
            "email": "abdullah@amonic.com",
            "password": "password",
            "firstname": "Abdullah",
            "lastname": "Al Thani",
            "birthdate": datetime.datetime(1988, 11, 5),
            "active": True
        },
        # Bahrain - неактивный пользователь (красный)
        {
            "office": "Bahrain",
            "role": user_role,
            "email": "hasan@amonic.com",
            "password": "password",
            "firstname": "Hasan",
            "lastname": "Al Bahrani",
            "birthdate": datetime.datetime(1991, 7, 20),
            "active": False
        },
        # Doha - неактивный пользователь (красный)
        {
            "office": "Doha",
            "role": user_role,
            "email": "maryam@amonic.com",
            "password": "password",
            "firstname": "Maryam",
            "lastname": "Al Qatari",
            "birthdate": datetime.datetime(1993, 4, 12),
            "active": False
        }
    ]
    
    # Добавляем пользователей, если они еще не существуют
    added_count = 0
    for user_data in users_to_add:
        if user_data["email"] not in existing_emails:
            office = office_dict.get(user_data["office"])
            if not office:
                print(f"Офис {user_data['office']} не найден. Пропускаем пользователя {user_data['email']}")
                continue
                
            user = User(
                office_id=office.id,
                role_id=user_data["role"].id,
                email=user_data["email"],
                password=user_data["password"],
                firstname=user_data["firstname"],
                lastname=user_data["lastname"],
                birthdate=user_data["birthdate"],
                active=user_data["active"]
            )
            session.add(user)
            added_count += 1
    
    if added_count > 0:
        session.commit()
        print(f"Добавлено {added_count} новых пользователей")
    else:
        print("Новые пользователи не добавлены (возможно, они уже существуют)")
    
    # Выводим список всех пользователей
    all_users = session.query(User).all()
    print("\nСписок всех пользователей:")
    for user in all_users:
        office_name = user.office.title if user.office else "Нет офиса"
        status = "Активен" if user.active else "Неактивен"
        print(f"- {user.firstname} {user.lastname} ({user.email}), Офис: {office_name}, Статус: {status}")

if __name__ == "__main__":
    add_users()

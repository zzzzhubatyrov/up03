from app.config.database import get_session
from app.models import Office, Country

def add_offices():
    """Добавление офисов в базу данных"""
    session = get_session()
    
    # Проверяем, существует ли страна
    country = session.query(Country).first()
    if not country:
        country = Country(name="United Arab Emirates")
        session.add(country)
        session.commit()
    
    # Проверяем, существуют ли уже офисы
    existing_offices = session.query(Office).all()
    existing_office_titles = [office.title for office in existing_offices]
    
    # Список офисов для добавления
    offices_to_add = [
        {"title": "Abu Dhabi", "phone": "+971-2-1234567", "contact": "Ahmed Al Mansouri"},
        {"title": "Bahrain", "phone": "+973-1-1234567", "contact": "Mohammed Al Khalifa"},
        {"title": "Doha", "phone": "+974-4-1234567", "contact": "Abdullah Al Thani"}
    ]
    
    # Добавляем офисы, если они еще не существуют
    added_count = 0
    for office_data in offices_to_add:
        if office_data["title"] not in existing_office_titles:
            office = Office(
                country_id=country.id,
                title=office_data["title"],
                phone=office_data["phone"],
                contact=office_data["contact"]
            )
            session.add(office)
            added_count += 1
    
    if added_count > 0:
        session.commit()
        print(f"Добавлено {added_count} новых офисов")
    else:
        print("Новые офисы не добавлены (возможно, они уже существуют)")
    
    # Выводим список всех офисов
    all_offices = session.query(Office).all()
    print("\nСписок всех офисов:")
    for office in all_offices:
        print(f"- {office.title} (ID: {office.id})")

if __name__ == "__main__":
    add_offices()

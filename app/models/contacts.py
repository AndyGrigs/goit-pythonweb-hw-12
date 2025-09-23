"""
Моделі контактів для системи управління контактами.

Цей модуль містить SQLAlchemy модель для роботи з контактами користувачів,
включаючи особисту інформацію та зв'язки з власниками.
"""

from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base


class Contact(Base):
    """
    Модель контакту в системі управління контактами.
    
    Кожен контакт належить конкретному користувачу (owner) і містить
    особисту інформацію для зв'язку та додаткові дані.
    
    Attributes:
        id (int): Унікальний ідентифікатор контакту
        first_name (str): Ім'я контакту (обов'язкове, до 50 символів)
        last_name (str): Прізвище контакту (обов'язкове, до 50 символів)
        email (str): Email адреса контакту (унікальна, до 100 символів)
        phone_number (str): Телефонний номер контакту (до 20 символів)
        birth_date (date): Дата народження контакту
        additional_data (str, optional): Додаткові дані про контакт
        owner_id (int): ID власника контакту (зовнішній ключ)
        owner (relationship): Зв'язок з власником контакту
        
    Note:
        Email адреса повинна бути унікальною в межах всієї системи.
        Контакти автоматично видаляються при видаленні власника.
        
    Example:
        >>> from datetime import date
        >>> contact = Contact(
        ...     first_name='Іван',
        ...     last_name='Петренко',
        ...     email='ivan@example.com',
        ...     phone_number='+380501234567',
        ...     birth_date=date(1990, 5, 15),
        ...     owner_id=1
        ... )
        >>> contact.full_name
        'Іван Петренко'
    """
    
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True,
               doc="Унікальний ідентифікатор контакту")
    
    first_name = Column(String(50), nullable=False, index=True,
                       doc="Ім'я контакту (обов'язкове, індексоване для пошуку)")
    
    last_name = Column(String(50), nullable=False, index=True,
                      doc="Прізвище контакту (обов'язкове, індексоване для пошуку)")
    
    email = Column(String(100), unique=True, nullable=False, index=True,
                  doc="Email адреса контакту (унікальна, індексована)")
    
    phone_number = Column(String(20), nullable=False,
                         doc="Телефонний номер контакту")
    
    birth_date = Column(Date, nullable=False,
                       doc="Дата народження контакту")
    
    additional_data = Column(Text, nullable=True,
                           doc="Додаткові дані про контакт (необов'язково)")

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False,
                     doc="ID власника контакту (зовнішній ключ на users.id)")
    
    owner = relationship("User", back_populates="contacts",
                        doc="Власник контакту (користувач системи)")
    
    @property
    def full_name(self) -> str:
        """
        Повне ім'я контакту (ім'я + прізвище).
        
        Returns:
            str: Повне ім'я у форматі "Ім'я Прізвище"
            
        Example:
            >>> contact = Contact(first_name='Іван', last_name='Петренко')
            >>> contact.full_name
            'Іван Петренко'
        """
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> Optional[int]:
        """
        Вік контакту в роках на поточну дату.
        
        Returns:
            Optional[int]: Вік в роках або None якщо дата народження у майбутньому
            
        Example:
            >>> from datetime import date
            >>> contact = Contact(birth_date=date(1990, 5, 15))
            >>> contact.age  # якщо поточний рік 2025
            35
        """
        from datetime import date
        today = date.today()
        
        if self.birth_date > today:
            return None
            
        age = today.year - self.birth_date.year
        
        # Перевіряємо чи вже був день народження цього року
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
            
        return age
    
    def days_until_birthday(self) -> int:
        """
        Кількість днів до наступного дня народження.
        
        Returns:
            int: Кількість днів (0 якщо день народження сьогодні)
            
        Example:
            >>> from datetime import date
            >>> contact = Contact(birth_date=date(1990, 12, 31))
            >>> # Якщо сьогодні 25 грудня
            >>> contact.days_until_birthday()
            6
        """
        from datetime import date
        today = date.today()
        
        # Створюємо дату дня народження в поточному році
        this_year_birthday = self.birth_date.replace(year=today.year)
        
        if this_year_birthday >= today:
            # День народження ще не був цього року
            return (this_year_birthday - today).days
        else:
            # День народження вже був, розраховуємо для наступного року
            next_year_birthday = self.birth_date.replace(year=today.year + 1)
            return (next_year_birthday - today).days
    
    def __repr__(self) -> str:
        """
        Строкове представлення контакту для відладки.
        
        Returns:
            str: Строкове представлення об'єкта
            
        Example:
            >>> contact = Contact(id=1, first_name='Іван', last_name='Петренко')
            >>> repr(contact)
            "<Contact(id=1, name='Іван Петренко', email='ivan@example.com')>"
        """
        return f"<Contact(id={self.id}, name='{self.full_name}', email='{self.email}')>"
    
    def to_dict(self) -> dict:
        """
        Конвертує об'єкт контакту в словник.
        
        Returns:
            dict: Словник з усіма даними контакту
            
        Example:
            >>> contact = Contact(first_name='Іван', last_name='Петренко')
            >>> contact_dict = contact.to_dict()
            >>> contact_dict['first_name']
            'Іван'
        """
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone_number': self.phone_number,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'additional_data': self.additional_data,
            'owner_id': self.owner_id,
            'full_name': self.full_name,
            'age': self.age
        }
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, extract
from app.models.contacts import Contact
from app.schemas.contacts import ContactCreate, ContactUpdate
from datetime import date, timedelta

def get_contact(db: Session, contact_id: int, owner_id: int) -> Optional[Contact]:
    """Отримання контакту за ID (тільки власника)"""
    return db.query(Contact).filter(
        Contact.id == contact_id, 
        Contact.owner_id == owner_id
    ).first()

def get_contacts(
    db: Session, 
    owner_id: int,
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None
) -> List[Contact]:
    """Отримання контактів користувача"""
    query = db.query(Contact).filter(Contact.owner_id == owner_id)
    
    if search:
        search_filter = or_(
            Contact.first_name.ilike(f"%{search}%"),
            Contact.last_name.ilike(f"%{search}%"),
            Contact.email.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    return query.offset(skip).limit(limit).all()

def create_contact(db: Session, contact: ContactCreate, owner_id: int) -> Contact:
    """Створення нового контакту"""
    db_contact = Contact(**contact.model_dump(), owner_id=owner_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def update_contact(
    db: Session, 
    contact_id: int, 
    contact_update: ContactUpdate, 
    owner_id: int
) -> Optional[Contact]:
    """Оновлення контакту"""
    db_contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.owner_id == owner_id
    ).first()
    
    if not db_contact:
        return None
    
    update_data = contact_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_contact, field, value)

    db.commit()
    db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int, owner_id: int) -> bool:
    """Видалення контакту"""
    db_contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.owner_id == owner_id
    ).first()
    
    if not db_contact:
        return False
    
    db.delete(db_contact)
    db.commit()
    return True

def get_contacts_with_upcoming_birthdays(db: Session, owner_id: int) -> List[Contact]:
    """Отримання контактів з днями народження на найближчі 7 днів"""
    today = date.today()
    next_week = today + timedelta(days=7)
    
    query = db.query(Contact).filter(Contact.owner_id == owner_id)
    
    if today.year == next_week.year:
        return query.filter(
            and_(
                extract('month', Contact.birth_date) >= today.month,
                extract('month', Contact.birth_date) <= next_week.month,
                or_(
                    extract('month', Contact.birth_date) > today.month,
                    and_(
                        extract('month', Contact.birth_date) == today.month, 
                        extract('day', Contact.birth_date) >= today.day 
                    )
                ),
                or_(
                    extract('month', Contact.birth_date) < next_week.month, 
                    and_(
                        extract('month', Contact.birth_date) == next_week.month,
                        extract('day', Contact.birth_date) <= next_week.day 
                    )
                )
            )
        ).all()
    else:
        return query.filter(
            or_(
                and_(
                    extract('month', Contact.birth_date) == today.month,
                    extract('day', Contact.birth_date) >= today.day
                ), 
                and_(
                    extract('month', Contact.birth_date) == next_week.month,
                    extract('day', Contact.birth_date) <= next_week.day
                )
            )
        ).all()
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db
from app.crud.contacts import (  # виправлено імпорт
    get_contact,
    get_contacts,
    create_contact,
    update_contact,
    delete_contact,
    get_contacts_with_upcoming_birthdays
)
from app.schemas.contacts import ContactCreate, ContactUpdate, ContactResponse

router = APIRouter()

@router.post("/", response_model=ContactResponse, status_code=201)
def create_contact_endpoint(
    contact: ContactCreate, 
    db: Session = Depends(get_db)
):
    """Створити новий контакт"""
    try:
        return create_contact(db=db, contact=contact)
    except Exception as e:
        if "unique constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="Email is already in the system")
        raise HTTPException(status_code=400, detail="Error creating contact")

@router.get("/", response_model=List[ContactResponse])
def read_contacts(
    skip: int = Query(0, ge=0, description="Amount of queries for skipping"),
    limit: int = Query(100, ge=1, le=500, description="Max amount of records"),
    search: Optional[str] = Query(None, description="Search with a name or email"),
    db: Session = Depends(get_db)
):
    """Отримати список контактів"""
    contacts = get_contacts(db, skip=skip, limit=limit, search=search)
    return contacts

@router.get("/birthdays/", response_model=List[ContactResponse])
def read_upcoming_birthdays(db: Session = Depends(get_db)):
    """Отримати контакти з днями народження на найближчі 7 днів"""
    contacts = get_contacts_with_upcoming_birthdays(db)
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    """Отримати контакт за ID"""
    db_contact = get_contact(db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found!")
    return db_contact

@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact_endpoint(
    contact_id: int, 
    contact_update: ContactUpdate, 
    db: Session = Depends(get_db)
):
    """Оновити контакт"""
    db_contact = update_contact(db, contact_id=contact_id, contact_update=contact_update)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found!")
    return db_contact

@router.delete("/{contact_id}")
def delete_contact_endpoint(contact_id: int, db: Session = Depends(get_db)):
    """Видалити контакт"""
    success = delete_contact(db, contact_id=contact_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found!")
    return {"message": "Contact deleted successfully!"}
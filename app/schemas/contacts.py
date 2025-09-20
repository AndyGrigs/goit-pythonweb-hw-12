from pydantic import BaseModel, EmailStr, validator
from datetime import date
from typing import Optional

class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birth_date: date
    additional_data: Optional[str] = None

    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Field should not be ampty!")
        return v.strip().title()

@validator('phone_number')
def validate_phone(cls, v):
    import re
    phone_pattern = re.compile(r'^[\+]?[1-9][\d\s\-\(\)]{8,15}$')
    if not phone_pattern.match(v.replace(' ', '')):
        raise ValueError("Wrong phone number format!")
    return v
    
class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    birth_date: Optional[date] = None
    additional_data: Optional[str] = None

    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip().title() if v else v
    
class ContactResponse(ContactBase):
    id: int
    owner_id: int
    class Config:
        from_attributes = True

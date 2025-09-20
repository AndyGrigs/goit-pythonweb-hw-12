from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False, index=True)
    last_name = Column(String(50), nullable=False, index=True)
    email = Column(String(100), unique=True,nullable=False, index=True)
    phone_number = Column(String(20), nullable=False)
    birth_date = Column(Date, nullable=False)
    additional_data= Column(Text, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="contacts")
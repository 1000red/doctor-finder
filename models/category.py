from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.base import Base


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    image = Column(String(500), nullable=True)

    doctors = relationship("Doctor", back_populates="category")
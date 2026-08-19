from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db.base import Base


class User(Base):
    __tablename__ = "users"

    user_id  = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name     = Column(String(100), nullable=False)
    last_name    =  Column(String(100), nullable=False)
    email    = Column(String(100), nullable=False, unique=True, index=True)
    google_id = Column(String(255), nullable=True, unique=True)
    password = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    gender = Column(String(20), nullable=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    doctor_reviews = relationship("DoctorReview", back_populates="user")
    doctor_favorites = relationship("DoctorFavorite", back_populates="user")


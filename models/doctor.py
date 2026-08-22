from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from db.base import Base


class Doctor(Base):
    __tablename__ = "doctors"

    doctor_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    image = Column(String(500), nullable=True)
    work_place = Column(String(200), nullable=True)
    experience = Column(Integer, nullable=True)
    treated = Column(Integer, default=0, nullable=False)
    price = Column(Float, nullable=False)
    average_rating = Column(Float, nullable=False, default=0.0)
    is_active = Column(Boolean, default=True, nullable=False)

    category_id  = Column(Integer, ForeignKey("categories.category_id"), nullable=False)

    availability = relationship("DoctorAvailability", back_populates="doctor")
    reviews = relationship("DoctorReview", back_populates="doctor")
    category = relationship("Category", back_populates="doctors")
    favorites = relationship("DoctorFavorite", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")

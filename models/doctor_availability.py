from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base


class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"

    availability_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    day_of_week = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    start_time = Column(String(5), nullable=False)
    end_time = Column(String(5), nullable=False)
    is_available = Column(Boolean, nullable=False, default=True)

    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=False)
    

    doctor = relationship("Doctor", back_populates="availability")
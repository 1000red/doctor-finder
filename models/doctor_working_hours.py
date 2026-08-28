from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from db.base import Base


class DoctorWorkingHours(Base):
    __tablename__ = "doctor_working_hours"
    __table_args__ = (
        CheckConstraint("day_of_week >= 0 AND day_of_week <= 6", name="ck_doctor_working_hours_day"),
        UniqueConstraint("doctor_id", "day_of_week", name="uq_doctor_working_hours_doctor_day"),
    )

    working_hours_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(String(5), nullable=False)
    end_time = Column(String(5), nullable=False)

    doctor = relationship("Doctor", back_populates="working_hours")

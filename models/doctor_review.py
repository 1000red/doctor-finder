from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from db.base import Base


class DoctorReview(Base):
    __tablename__ = "doctor_reviews"

    review_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)

    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    doctor_id = Column(Integer,ForeignKey("doctors.doctor_id"),nullable=False)

    user = relationship("User", back_populates="doctor_reviews")
    doctor = relationship("Doctor", back_populates="reviews")
    reviews = relationship("DoctorReview", back_populates="doctor")
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint, func
from sqlalchemy.orm import relationship
from db.base import Base


class DoctorFavorite(Base):
    __tablename__ = "doctor_favorites"

    favorite_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "doctor_id", name="uq_user_doctor_favorite"),
    )

    user = relationship("User", back_populates="doctor_favorites")
    doctor = relationship("Doctor", back_populates="favorites")
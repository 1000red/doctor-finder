from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.doctor_working_hours import DoctorWorkingHours
from schemas.doctor_working_hours import DoctorWorkingHoursCreate
from services.doctor_service import get_doctor_by_id


def get_doctor_working_hours(db: Session, doctor_id: int) -> list[DoctorWorkingHours]:
    get_doctor_by_id(db, doctor_id)
    return (
        db.query(DoctorWorkingHours)
        .filter(DoctorWorkingHours.doctor_id == doctor_id)
        .order_by(DoctorWorkingHours.day_of_week)
        .all()
    )


def replace_doctor_working_hours(
    db: Session,
    doctor_id: int,
    hours: list[DoctorWorkingHoursCreate],
) -> list[DoctorWorkingHours]:
    """Replace a doctor's complete weekly schedule in one request."""
    get_doctor_by_id(db, doctor_id)

    days = [item.day_of_week for item in hours]
    if len(days) != len(set(days)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only one working-hours range is allowed for each day",
        )

    try:
        db.query(DoctorWorkingHours).filter(
            DoctorWorkingHours.doctor_id == doctor_id
        ).delete(synchronize_session=False)

        schedules = [
            DoctorWorkingHours(
                doctor_id=doctor_id,
                day_of_week=item.day_of_week,
                start_time=item.start_time,
                end_time=item.end_time,
            )
            for item in hours
        ]
        db.add_all(schedules)
        db.commit()

        for schedule in schedules:
            db.refresh(schedule)
        return schedules
    except Exception:
        db.rollback()
        raise

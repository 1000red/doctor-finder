"""
Seed script to populate doctor_reviews with random ratings,
then recalculate each doctor's average_rating.

Run with: python -m db.add_db.add_reviews
"""

import random

from sqlalchemy import func
from datetime import datetime, timezone

from db.database import SessionLocal
from models.doctor import Doctor
from models.doctor_review import DoctorReview
from models.user import User

MIN_REVIEWS_PER_DOCTOR = 3
MAX_REVIEWS_PER_DOCTOR = 15


def seed_reviews():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            print("No users found in the database. Please seed users first.")
            return

        user_ids = [u.user_id for u in users]

        doctors = db.query(Doctor).all()
        if not doctors:
            print("No doctors found in the database. Please seed doctors first.")
            return

        total_reviews_added = 0

        for doctor in doctors:
            review_count = random.randint(MIN_REVIEWS_PER_DOCTOR, MAX_REVIEWS_PER_DOCTOR)
            review_count = min(review_count, len(user_ids))  # can't exceed available users
            chosen_user_ids = random.sample(user_ids, review_count)

            for uid in chosen_user_ids:
                rating = random.randint(1, 5)
                review = DoctorReview(
                    user_id=uid,
                    doctor_id=doctor.doctor_id,
                    rating=rating,
                    created_at=datetime.now(timezone.utc),   # <-- ضيف السطر ده
                )
                db.add(review)
                total_reviews_added += 1

            # Recalculate this doctor's average rating
            db.flush()  # push the reviews we just added so avg() sees them
            average = (
                db.query(func.avg(DoctorReview.rating))
                .filter(DoctorReview.doctor_id == doctor.doctor_id)
                .scalar()
            )
            doctor.average_rating = round(average, 2) if average is not None else 0.0

            print(f"Doctor {doctor.doctor_id} ({doctor.name}): {review_count} reviews, avg={doctor.average_rating}")

        db.commit()
        print(f"\nDone. Total reviews added: {total_reviews_added}")

    except Exception as e:
        db.rollback()
        print(f"Error while seeding reviews: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_reviews()
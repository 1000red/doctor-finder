"""
Seed script to populate doctor_reviews with random ratings,
then recalculate each doctor's average_rating.
If no users exist, fake users are created first.

Run with: python -m db.add_db.add_reviews
"""

from datetime import datetime, timezone
import random

from sqlalchemy import func

from db.database import SessionLocal
from models.doctor import Doctor
from models.doctor_review import DoctorReview
from models.user import User

MIN_REVIEWS_PER_DOCTOR = 3
MAX_REVIEWS_PER_DOCTOR = 15
FAKE_USERS_COUNT = 50

FAKE_NAMES = [
    "Ahmed Ali", "Mona Hassan", "Youssef Ibrahim", "Sara Mahmoud", "Omar Saeed",
    "Nada Fathy", "Karim Adel", "Heba Tarek", "Amir Nabil", "Dina Kamal",
    "Mostafa Ramadan", "Yasmine Salah", "Tarek Fawzy", "Rania Samir", "Hesham Mounir",
    "Salma Raafat", "Adel Hassan", "Menna Ibrahim", "Sherif Nour", "Farida Amin",
]


def _random_email(name: str, index: int) -> str:
    slug = name.lower().replace(" ", ".")
    return f"{slug}{index}@example.com"


def ensure_fake_users(db) -> list[int]:
    existing_count = db.query(User).count()
    if existing_count > 0:
        return [u.user_id for u in db.query(User).all()]

    print(f"No users found. Creating {FAKE_USERS_COUNT} fake users...")

    created_ids = []
    for i in range(FAKE_USERS_COUNT):
        name = random.choice(FAKE_NAMES)
        user = User(
            full_name=name,
            email=_random_email(name, i),
            password="hashed_placeholder",  # dummy value, not a real login
            phone=None,
            gender=random.choice(["male", "female"]),
            is_deleted=False,
        )
        db.add(user)

    db.flush()  # assign ids without committing yet
    created_ids = [u.user_id for u in db.query(User).all()]
    print(f"Created {len(created_ids)} fake users.")
    return created_ids


def seed_reviews():
    db = SessionLocal()
    try:
        user_ids = ensure_fake_users(db)

        doctors = db.query(Doctor).all()
        if not doctors:
            print("No doctors found in the database. Please seed doctors first.")
            db.rollback()
            return

        total_reviews_added = 0

        for doctor in doctors:
            review_count = random.randint(MIN_REVIEWS_PER_DOCTOR, MAX_REVIEWS_PER_DOCTOR)
            review_count = min(review_count, len(user_ids))
            chosen_user_ids = random.sample(user_ids, review_count)

            for uid in chosen_user_ids:
                rating = random.randint(1, 5)
                review = DoctorReview(
                    user_id=uid,
                    doctor_id=doctor.doctor_id,
                    rating=rating,
                    created_at=datetime.now(timezone.utc),
                )
                db.add(review)
                total_reviews_added += 1

            db.flush()
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
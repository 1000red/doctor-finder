"""
Seed script to populate the doctors table with ~20 doctors per category.
Run with: python seed_doctors.py
"""

import random

from db.database import SessionLocal
from models.category import Category
from models.doctor import Doctor

DOCTORS_PER_CATEGORY = 20

# doctor_6.png is a female doctor's photo — reserve it for female names only
FEMALE_IMAGE = "doctor/doctor_6.png"
MALE_IMAGES = [
    "doctor/doctor_1.png",
    "doctor/doctor_2.png",
    "doctor/doctor_3.png",
    "doctor/doctor_4.png",
    "doctor/doctor_5.png",
    "doctor/doctor_7.png",
]

MALE_NAMES = [
    "Ahmed Samir",
    "Mohamed Abdullah",
    "Khaled Ibrahim",
    "Omar Hassan",
    "Youssef Tarek",
    "Mostafa Kamal",
    "Karim Fathy",
    "Amir Ramadan",
    "Sherif Adel",
    "Wael Mounir",
    "Tarek Saeed",
    "Hesham Fawzy",
    "Amr Nabil",
    "Bassem Raafat",
    "Moataz Salah",
]

FEMALE_NAMES = [
    "Mona Ibrahim",
    "Sara Adel",
    "Yasmine Tarek",
    "Heba Allah Mohamed",
    "Dina Samir",
    "Nour El-Din",
    "Rana Fathy",
    "Mariam Hassan",
    "Eman Salah",
    "Shereen Nabil",
]

WORK_PLACES = [
    "Dar Al-Shifa Hospital",
    "Al Noor Hospital",
    "Specialized Medical Center",
    "Al Salam International Hospital",
    "Al Amal Clinics",
    "Maadi Specialized Hospital",
    "Modern Medical Complex",
    "Al Hayat Hospital",
    "Medical Care Center",
]


def build_doctor_name(base_name: str, category_name: str) -> str:
    return f"DR. {base_name} - Consultant {category_name}"


def get_random_doctor(used_names: set) -> tuple[str, str]:
    """Returns (name, image_path), avoiding name repetition."""
    is_female = random.random() < 0.2

    names_pool = FEMALE_NAMES if is_female else MALE_NAMES
    image = FEMALE_IMAGE if is_female else random.choice(MALE_IMAGES)

    available = [n for n in names_pool if n not in used_names]
    if not available:
        available = names_pool  # اسمح بالتكرار لو خلصت الأسامي

    name = random.choice(available)
    used_names.add(name)
    return name, image


def seed_doctors():
    db = SessionLocal()
    try:
        categories = db.query(Category).all()
        if not categories:
            print(f"Added {DOCTORS_PER_CATEGORY} doctors for category: {category.name}")
            return

        total_added = 0

        for category in categories:
            used_names = set()
            for _ in range(DOCTORS_PER_CATEGORY):
                base_name, image = get_random_doctor(used_names)

                doctor = Doctor(
                    name=build_doctor_name(base_name, category.name),
                    image=image,
                    work_place=random.choice(WORK_PLACES),
                    experience=random.randint(2, 25),
                    treated=random.randint(20, 2000),
                    price=float(random.choice([100, 150, 200, 250, 300, 350, 400, 500])),
                    average_rating=0.0,
                    is_active=True,
                    category_id=category.category_id,
                )
                db.add(doctor)
                total_added += 1

            print(f"Added {DOCTORS_PER_CATEGORY} doctors for category: {category.name}")

        db.commit()
        print(f"\nDone. Total doctors added: {total_added}")

    except Exception as e:
        db.rollback()
        print(f"Error while seeding doctors: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_doctors()
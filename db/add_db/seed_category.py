from db.database import SessionLocal
from models.category import Category

CATEGORIES = [
    "Cardiology",
    "Dermatology",
    "Gastroenterology",
    "Gynecology",
    "Neurology",
    "Ophthalmology",
    "Orthopedics",
    "Pediatrics",
    "Psychiatry",
    "Urology",
]


def seed_categories():
    db = SessionLocal()
    try:
        added = 0
        skipped = 0

        for name in CATEGORIES:
            existing = db.query(Category).filter(Category.name == name).first()
            if existing:
                print(f"Skipped (already exists): {name}")
                skipped += 1
                continue

            category = Category(
                name=name,
                image=f"category/{name}.svg",
            )
            db.add(category)
            added += 1
            print(f"Added: {name}")

        db.commit()
        print(f"\nDone. Added: {added}, Skipped: {skipped}")

    except Exception as e:
        db.rollback()
        print(f"Error while seeding categories: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_categories()
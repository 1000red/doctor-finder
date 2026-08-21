from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.category import Category


def get_category_by_id(db: Session, category_id: int) -> Category:
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


def get_categories(db: Session) -> list[Category]:
    return db.query(Category).all()
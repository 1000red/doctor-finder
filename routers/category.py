from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.category import CategoryOut
from services import get_categories, get_category_by_id

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=list[CategoryOut])
def get_all_categories(
    request: Request,
    db: Session = Depends(get_db),
):
    categories = get_categories(db)
    base_url = str(request.base_url).rstrip("/")

    result = []
    for category in categories:
        image_url = f"{base_url}/image/{category.image}" if category.image else None
        result.append(
            CategoryOut(
                category_id=category.category_id,
                name=category.name,
                image=image_url,
            )
        )
    return result


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(
    category_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    category = get_category_by_id(db, category_id)

    base_url = str(request.base_url).rstrip("/")
    image_url = f"{base_url}/image/{category.image}" if category.image else None

    return CategoryOut(
        category_id=category.category_id,
        name=category.name,
        image=image_url,
    )
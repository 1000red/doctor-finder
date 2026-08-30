from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.category import CategoryOut
from services.category_service import get_categories

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
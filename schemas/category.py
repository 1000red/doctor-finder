from pydantic import BaseModel
from typing import Optional


class CategoryOut(BaseModel):
    category_id: int
    name: str
    image: Optional[str] = None

    model_config = {"from_attributes": True}
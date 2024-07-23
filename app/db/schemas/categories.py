from typing import List, Optional

from pydantic import BaseModel, Field

from app.db.schemas.items import Item
from app.utils import datetime


class CategoryBase(BaseModel):
    name: str = Field(min_length=2, max_length=100, examples=["books"])
    notes: str = Field(default="", examples=["default category"])


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(min_length=2, max_length=100, default=None)
    notes: Optional[str] = Field(default=None)


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    category_id: int
    row_update_time: datetime

    total_amount_seller_sold: Optional[float] = Field(default=0.0)
    total_quantity_seller_sold: Optional[int] = Field(default=0)
    total_amount_member_sold: Optional[float] = Field(default=0.0)
    total_quantity_member_sold: Optional[int] = Field(default=0)

    class Config:
        orm_mode: True

class CategoryView(Category):
    items: List[Item] = []

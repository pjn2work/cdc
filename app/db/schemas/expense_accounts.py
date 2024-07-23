from typing import List, Optional

from pydantic import BaseModel, Field

from app.db.schemas.seller_items import SellerItems
from app.utils import datetime


class ExpenseAccountBase(BaseModel):
    name: str = Field(min_length=2, max_length=100, examples=["only cash account"])
    notes: str = Field(default="", examples=["default account"])


class ExpenseAccountUpdate(BaseModel):
    name: Optional[str] = Field(min_length=2, max_length=100, default=None)
    notes: Optional[str] = Field(default=None)


class ExpenseAccountCreate(ExpenseAccountBase):
    pass


class ExpenseAccount(ExpenseAccountBase):
    ea_id: int
    row_update_time: datetime

    total_amount_seller_sold: Optional[float] = Field(default=0.0)
    total_quantity_seller_sold: Optional[int] = Field(default=0)

    class Config:
        orm_mode: True


class ExpenseAccountView(ExpenseAccount):
    seller_items: List[SellerItems] = []

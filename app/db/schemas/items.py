from typing import List, Optional

from pydantic import BaseModel, Field

from .member_items import MemberItems
from .seller_items import SellerItems
from ...utils import date, datetime


class ItemBase(BaseModel):
    seller_id: int
    item_id: int
    ea_id: int

    quantity: int = Field(ge=1)
    total_price: float = Field(ge=0.0)
    notes: str = Field(default="", examples=["default account"])
    sell_date: date


class ItemUpdate(BaseModel):
    seller_id: Optional[int] = Field(default=None)
    item_id: Optional[int] = Field(default=None)
    ea_id: Optional[int] = Field(default=None)

    quantity: Optional[int] = Field(ge=1, default=None)
    total_price: Optional[float] = Field(ge=0.0, default=None)
    notes: Optional[str] = Field(default=None)
    sell_date: Optional[date] = Field(default=None)


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    item_id: int
    row_update_time: datetime

    class Config:
        orm_mode: True


class ItemView(Item):
    seller_items: List[SellerItems] = []
    member_items: List[MemberItems] = []

    total_amount_seller_sold: Optional[float] = Field(default=0.0)
    total_quantity_seller_sold: Optional[int] = Field(default=0)
    total_amount_member_sold: Optional[float] = Field(default=0.0)
    total_quantity_member_sold: Optional[int] = Field(default=0)

# ----------------------------------------------------------


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

    class Config:
        orm_mode: True

class CategoryView(Category):
    items: List[Item] = []

from typing import List, Optional

from pydantic import BaseModel, Field

from .member_items import MemberItems
from .seller_items import SellerItems
from ...utils import date, datetime


class ItemsBase(BaseModel):
    seller_id: int
    item_id: int
    ea_id: int

    quantity: int = Field(ge=1)
    total_price: float = Field(ge=0.0)
    notes: str = Field(default="", examples=["default account"])
    sell_date: date


class ItemsUpdate(BaseModel):
    seller_id: Optional[int] = Field(default=None)
    item_id: Optional[int] = Field(default=None)
    ea_id: Optional[int] = Field(default=None)

    quantity: Optional[int] = Field(ge=1, default=None)
    total_price: Optional[float] = Field(ge=0.0, default=None)
    notes: Optional[str] = Field(default=None)
    sell_date: Optional[date] = Field(default=None)


class ItemsCreate(ItemsBase):
    pass


class Items(ItemsBase):
    item_id: int
    row_update_time: datetime

    seller_items: List[SellerItems] = []
    member_items: List[MemberItems] = []

    class Config:
        orm_mode: True


# ----------------------------------------------------------


class CategoriesBase(BaseModel):
    name: str = Field(min_length=2, max_length=100, examples=["books"])
    notes: str = Field(default="", examples=["default category"])


class CategoriesUpdate(BaseModel):
    name: Optional[str] = Field(min_length=2, max_length=100, default=None)
    notes: Optional[str] = Field(default=None)


class CategoriesCreate(CategoriesBase):
    pass


class Categories(CategoriesBase):
    category_id: int
    row_update_time: datetime

    items: List[Items] = []

    class Config:
        orm_mode: True
from typing import Optional

from pydantic import BaseModel, Field

from ...utils import date, datetime


class SellerItemsBase(BaseModel):
    seller_id: int
    item_id: int
    ea_id: int

    quantity: int = Field(ge=1)
    total_price: float = Field(ge=0.0)
    notes: str = Field(default="", examples=["default account"])
    sell_date: date


class SellerUpdate(BaseModel):
    seller_id: Optional[int] = Field(default=None)
    item_id: Optional[int] = Field(default=None)
    ea_id: Optional[int] = Field(default=None)

    quantity: Optional[int] = Field(ge=1, default=None)
    total_price: Optional[float] = Field(ge=0.0, default=None)
    notes: Optional[str] = Field(default=None)
    sell_date: Optional[date] = Field(default=None)


class SellerItemsCreate(SellerItemsBase):
    pass


class SellerItems(SellerItemsBase):
    tid: int
    row_update_time: datetime

    class Config:
        orm_mode: True

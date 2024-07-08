from typing import Optional

from pydantic import BaseModel, Field

from app.utils import date, datetime


class MemberItemsBase(BaseModel):
    member_id: int

    quantity: int = Field(ge=1)
    total_price: float = Field(ge=0.0)
    notes: str = Field(default="", examples=["first book"])
    buy_date: date
    is_cash: bool


class MemberItemsUpdate(BaseModel):
    member_id: Optional[int] = Field(default=None)
    item_id: Optional[int] = Field(default=None)

    quantity: Optional[int] = Field(ge=1, default=None)
    total_price: Optional[float] = Field(ge=0.0, default=None)
    notes: Optional[str] = Field(default=None)
    buy_date: Optional[date] = Field(default=None)
    is_cash: Optional[bool] = Field(default=None)


class MemberItemsCreate(MemberItemsBase):
    pass


class MemberItems(MemberItemsBase):
    tid: int
    item_id: int
    row_update_time: datetime

    class Config:
        orm_mode: True

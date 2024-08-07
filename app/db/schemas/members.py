from typing import List, Optional

from pydantic import BaseModel, Field, EmailStr

from app.db.schemas.member_donations import MemberDonation
from app.db.schemas.member_due_payment import MemberDuesPayment
from app.db.schemas.member_items import MemberItems
from app.utils import get_today, get_now, datetime, date, get_today_year_month_str


class MemberBase(BaseModel):
    start_date: date = Field(default_factory=get_today)
    is_active: bool = Field(default=True)
    amount: float = Field(ge=0.0, examples=[10])

    name: str = Field(min_length=3, max_length=100, examples=["Pedro Nunes"])
    tlf: str = Field(min_length=9, max_length=13, examples=["912000678"])
    email: Optional[EmailStr] = Field(examples=["pedro@gmail.com"])
    notes: str = Field(default="", examples=["IT member"])


class MemberBaseStats(MemberBase):
    total_months_missing: int = Field(default=0)
    total_amount_missing: float = Field(default=0.0)
    total_months_paid: int = Field(default=0)
    total_amount_paid: float = Field(default=0.0)

    total_quantity_bought: int = Field(default=0)
    total_amount_bought: float = Field(default=0.0)


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: Optional[str] = Field(min_length=3, max_length=100, default=None)
    tlf: Optional[str] = Field(min_length=9, max_length=13, default=None)
    email: Optional[EmailStr] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class MemberUpdateActive(BaseModel):
    since: str = Field(default_factory=get_today_year_month_str, examples=["2024-06"])
    is_active: bool = Field(default=False)


class MemberUpdateAmount(BaseModel):
    since: str = Field(default_factory=get_today_year_month_str, examples=["2024-06"])
    amount: float = Field(ge=0.0, examples=[5])


### Members History

class MemberHistoryBase(MemberBaseStats):
    member_id: int
    since: str = Field(default_factory=get_today_year_month_str)
    date_time: datetime = Field(default_factory=get_now)


### Main objects

class MemberHistory(MemberHistoryBase):
    tid: int

    class Config:
        orm_mode: True


class Member(MemberBaseStats):
    member_id: int

    class Config:
        orm_mode: True


class MemberView(Member):
    months_missing: List[str] = []

    member_history: List[MemberHistory] = []
    member_due_payment: List[MemberDuesPayment] = []
    member_donations: List[MemberDonation] = []
    member_items: List[MemberItems] = []

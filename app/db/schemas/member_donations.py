from typing import Optional

from pydantic import BaseModel, Field

from app.utils import datetime, date, get_today


class MemberDonationBase(BaseModel):
    amount: float = Field(ge=0.0)
    is_cash: bool = Field(default=False)
    pay_date: Optional[date] = Field(default_factory=get_today)


class MemberDonationCreate(MemberDonationBase):
    pass


class MemberDonation(MemberDonationCreate):
    tid: int
    member_id: int
    pay_update_time: datetime

    class Config:
        orm_mode: True

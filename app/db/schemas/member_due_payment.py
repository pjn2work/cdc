from typing import Optional

from pydantic import BaseModel, Field

from app.utils import datetime, date, get_today


class MemberDuesPaymentBase(BaseModel):
    amount: float = Field(ge=0.0)
    is_paid: bool = Field(default=False)
    is_member_active: bool = Field(default=True)
    is_cash: Optional[bool] = Field(default=None)
    pay_date: Optional[date] = Field(default=None)


class MemberDuesPaymentCreate(BaseModel):
    is_cash: bool = Field(default=False)
    pay_date: date = Field(default_factory=get_today)


class MemberDuesPayment(MemberDuesPaymentBase):
    tid: int
    member_id: int
    id_year_month: str
    pay_update_time: datetime

    class Config:
        orm_mode: True

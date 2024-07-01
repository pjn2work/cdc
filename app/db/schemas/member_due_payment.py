from typing import Optional
from pydantic import BaseModel, Field
from ...utils import datetime, date


class MemberDuesPaymentBase(BaseModel):
    amount: float = Field(ge=0.0)
    is_paid: bool = Field(default=False)
    is_member_active: bool = Field(default=True)
    pay_date: Optional[date] = Field(default=None)


class MemberDuesPaymentCreate(BaseModel):
    pay_date: date = Field(default_factory=date.today)


class MemberDuesPayment(MemberDuesPaymentBase):
    tid: int
    member_id: int
    id_year_month: str
    pay_update_time: datetime

    class Config:
        orm_mode: True

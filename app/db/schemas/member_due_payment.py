from pydantic import BaseModel, Field
from ...utils import datetime


class MemberDuesPaymentBase(BaseModel):
    amount: float = Field(ge=0.0)
    is_paid: bool = Field(default=False)
    is_member_active: bool = Field(default=True)


class MemberDuesPayment(MemberDuesPaymentBase):
    tid: int
    member_id: int
    id_year_month: str
    pay_date_time: datetime

    class Config:
        orm_mode: True

from typing import Optional, List

from pydantic import BaseModel, Field

from app.db.schemas.member_due_payment import MemberDuesPayment
from app.utils import date, format_year_month


class DuesPaymentBase(BaseModel):
    id_year_month: str = Field(examples=["2024-06"])


class DuesPaymentCreate(DuesPaymentBase):
    pass


class DuesPayment(DuesPaymentBase):
    date_ym: Optional[date] = None
    year: Optional[int] = None
    month: Optional[int] = None

    def model_post_init(self, __context):
        self.id_year_month = format_year_month(self.id_year_month)
        self.year, self.month = list(map(int, self.id_year_month.split('-')))
        self.date_ym = date(year=self.year, month=self.month, day=1)

    class Config:
        orm_mode: True


class DuesPaymentStats(DuesPayment):
    total_amount_paid: Optional[float] = Field(default=0.0)
    total_members_paid: Optional[int] = Field(default=0)
    total_amount_missing: Optional[float] = Field(default=0.0)
    total_members_missing: Optional[int] = Field(default=0)


class DuesPaymentView(DuesPaymentStats):
    member_due_payment: Optional[List[MemberDuesPayment]] = Field(default_factory=lambda :[])

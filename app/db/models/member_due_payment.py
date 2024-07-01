from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, UniqueConstraint, DateTime, Date
from sqlalchemy.orm import relationship
from ..database import Base


class MemberDuesPayment(Base):
    __tablename__ = "member_dues_payments"
    __table_args__ = (UniqueConstraint("member_id", "id_year_month", name="uix_1"), )
    tid = Column(Integer, primary_key=True, autoincrement=True, index=True)

    member_id = Column(Integer, ForeignKey("members.member_id"), index=True)
    id_year_month = Column(String, ForeignKey("dues_payments.id_year_month"), index=True)
    is_paid = Column(Boolean, default=False)
    is_member_active = Column(Boolean, default=True)
    amount = Column(Float)
    pay_date = Column(Date)
    pay_update_time = Column(DateTime)

    dues_payment = relationship("DuesPayment", back_populates="member_due_payment")
    member = relationship("Member", back_populates="member_due_payment")

from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, UniqueConstraint, DateTime, Date
from sqlalchemy.orm import relationship

from app.db.database import Base


class MemberDuesPayment(Base):
    __tablename__ = "member_dues_payments"
    __table_args__ = (UniqueConstraint("member_id", "id_year_month", name="uix_1"), )
    tid = Column(Integer, primary_key=True, autoincrement=True, index=True)

    member_id = Column(Integer, ForeignKey(column="members.member_id", onupdate="CASCADE", ondelete="CASCADE"), index=True)
    id_year_month = Column(String, ForeignKey(column="dues_payments.id_year_month", onupdate="CASCADE", ondelete="CASCADE"), index=True)
    is_paid = Column(Boolean, default=False)
    is_member_active = Column(Boolean, default=True)
    amount = Column(Float)
    is_cash = Column(Boolean)
    pay_date = Column(Date)
    pay_update_time = Column(DateTime)

    dues_payment = relationship("DuesPayment", back_populates="member_due_payment")
    member = relationship("Member", back_populates="member_due_payment")

from sqlalchemy import Column, Integer, Float, Boolean, String, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship

from ..database import Base


class MemberAbs(Base):
    __abstract__ = True

    start_date = Column(Date)
    is_active = Column(Boolean, index=True, default=True)
    amount = Column(Float)

    name = Column(String, index=True)
    tlf = Column(String)
    email = Column(String, default="")
    notes = Column(String, default="")

    total_months_missing = Column(Integer, default=0)
    total_amount_missing = Column(Float, default=0.0)
    total_months_paid = Column(Integer, default=0)
    total_amount_paid = Column(Float, default=0.0)


class Member(MemberAbs):
    __tablename__ = "members"
    member_id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    member_history = relationship("MemberHistory", back_populates="member")
    member_due_payment = relationship("MemberDuesPayment", back_populates="member")
    member_donations = relationship("MemberDonation", back_populates="member")
    member_items = relationship("MemberItems", back_populates="member")


class MemberHistory(MemberAbs):
    __tablename__ = "member_history"
    tid = Column(Integer, primary_key=True, autoincrement=True, index=True)

    member_id = Column(Integer, ForeignKey("members.member_id"), index=True)
    since = Column(String)
    date_time = Column(DateTime, index=True)

    member = relationship("Member", back_populates="member_history")

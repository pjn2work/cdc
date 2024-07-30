from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Date, Boolean
from sqlalchemy.orm import relationship

from app.db.database import Base


class MemberDonation(Base):
    __tablename__ = "member_donations"
    tid = Column(Integer, primary_key=True, autoincrement=True, index=True)

    member_id = Column(Integer, ForeignKey(column="members.member_id", onupdate="CASCADE", ondelete="CASCADE"), index=True)
    amount = Column(Float)
    is_cash = Column(Boolean)
    pay_date = Column(Date)
    pay_update_time = Column(DateTime)

    member = relationship("Member", back_populates="member_donations")

from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship

from ..database import Base


class MemberDonation(Base):
    __tablename__ = "member_donations"
    tid = Column(Integer, primary_key=True, autoincrement=True, index=True)

    member_id = Column(Integer, ForeignKey("members.member_id"), index=True)
    amount = Column(Float)
    pay_date = Column(Date)
    pay_update_time = Column(DateTime)

    member = relationship("Member", back_populates="member_donations")

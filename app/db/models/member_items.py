from sqlalchemy import Column, Integer, Float, String, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.db.database import Base


class MemberItems(Base):
    __tablename__ = "member_items"
    tid = Column(Integer, primary_key=True, autoincrement=True, index=True)

    member_id = Column(Integer, ForeignKey("members.member_id"), index=True)
    item_id = Column(Integer, ForeignKey("items.item_id"), index=True)

    quantity = Column(Integer)
    total_price = Column(Float)
    notes = Column(String, default="")
    buy_date = Column(Date)
    is_cash = Column(Boolean)
    row_update_time = Column(DateTime)

    member = relationship("Member", back_populates="member_items")
    items = relationship("Item", back_populates="member_items")

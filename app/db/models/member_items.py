from sqlalchemy import Column, Integer, Float, String, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.db.database import Base


class MemberItems(Base):
    __tablename__ = "member_items"
    tid = Column(Integer, primary_key=True, autoincrement=True, index=True)

    member_id = Column(Integer, ForeignKey(column="members.member_id", onupdate="CASCADE", ondelete="CASCADE"), index=True)
    item_id = Column(Integer, ForeignKey(column="items.item_id", onupdate="CASCADE", ondelete="CASCADE"), index=True)

    quantity = Column(Integer)
    total_price = Column(Float)
    notes = Column(String, default="")
    purchase_date = Column(Date)
    is_cash = Column(Boolean)
    row_update_time = Column(DateTime)

    member = relationship("Member", back_populates="member_items")
    item = relationship("Item", back_populates="member_items")

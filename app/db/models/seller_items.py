from sqlalchemy import Column, Integer, Float, String, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.db.database import Base


class SellerItems(Base):
    __tablename__ = "seller_items"
    tid = Column(Integer, primary_key=True, autoincrement=True, index=True)

    seller_id = Column(Integer, ForeignKey(column="sellers.seller_id", onupdate="CASCADE", ondelete="CASCADE"), index=True)
    item_id = Column(Integer, ForeignKey(column="items.item_id", onupdate="CASCADE", ondelete="CASCADE"), index=True)
    ea_id = Column(Integer, ForeignKey(column="expense_accounts.ea_id", onupdate="CASCADE", ondelete="CASCADE"), index=True)

    quantity = Column(Integer)
    total_price = Column(Float)
    notes = Column(String, default="")
    purchase_date = Column(Date)
    is_cash = Column(Boolean)
    row_update_time = Column(DateTime)

    seller = relationship("Seller", back_populates="seller_items")
    item = relationship("Item", back_populates="seller_items")
    expense_account = relationship("ExpenseAccount", back_populates="seller_items")

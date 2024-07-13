from sqlalchemy import Column, Integer, Float, String, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship

from app.db.database import Base


class SellerItems(Base):
    __tablename__ = "seller_items"
    tid = Column(Integer, primary_key=True, autoincrement=True, index=True)

    seller_id = Column(Integer, ForeignKey("sellers.seller_id"), index=True)
    item_id = Column(Integer, ForeignKey("items.item_id"), index=True)
    ea_id = Column(Integer, ForeignKey("expense_accounts.ea_id"), index=True)

    quantity = Column(Integer)
    total_price = Column(Float)
    notes = Column(String, default="")
    sell_date = Column(Date)
    row_update_time = Column(DateTime)

    sellers = relationship("Seller", back_populates="seller_items")
    items = relationship("Item", back_populates="seller_items")
    expense_accounts = relationship("ExpenseAccount", back_populates="seller_items")

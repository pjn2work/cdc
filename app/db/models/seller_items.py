from sqlalchemy import Column, Integer, Float, String, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship

from ..database import Base


class ExpenseAccount(Base):
    __tablename__ = "expense_accounts"
    ea_id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    name = Column(String, index=True)
    notes = Column(String, default="")
    row_update_time = Column(DateTime)

    seller_items = relationship("SellerItems", back_populates="expense_accounts")


class SellerItems(Base):
    __tablename__ = "seller_items"
    tid = Column(Integer, primary_key=True, autoincrement=True, index=True)

    seller_id = Column(Integer, ForeignKey("sellers.seller_id"), index=True)
    item_id = Column(String, ForeignKey("items.item_id"), index=True)
    ea_id = Column(String, ForeignKey("expense_accounts.ea_id"), index=True)

    quantity = Column(Integer)
    total_price = Column(Float)
    notes = Column(String, default="")
    sell_date = Column(Date)
    row_update_time = Column(DateTime)

    sellers = relationship("Sellers", back_populates="seller_items")
    items = relationship("Items", back_populates="seller_items")
    expense_accounts = relationship("ExpenseAccount", back_populates="seller_items")

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from ..database import Base


class Seller(Base):
    __tablename__ = "sellers"
    seller_id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    name = Column(String, index=True)
    tlf = Column(String)
    email = Column(String, default="")
    notes = Column(String, default="")

    seller_items = relationship("SellerItems", back_populates="sellers")


# ----------------------------------------------------------


class ExpenseAccount(Base):
    __tablename__ = "expense_accounts"
    ea_id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    name = Column(String, index=True)
    notes = Column(String, default="")
    row_update_time = Column(DateTime)

    seller_items = relationship("SellerItems", back_populates="expense_accounts")

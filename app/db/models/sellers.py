from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import relationship

from app.db.database import Base


class Seller(Base):
    __tablename__ = "sellers"
    seller_id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    name = Column(String, unique=True, nullable=False, index=True)
    tlf = Column(String)
    email = Column(String, default="")
    notes = Column(String, default="")
    row_update_time = Column(DateTime)

    total_amount_sold = Column(Float, default=0.0)
    total_quantity_sold = Column(Integer, default=0)

    seller_items = relationship("SellerItems", back_populates="seller")

from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import relationship

from app.db.database import Base


class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    name = Column(String, unique=True, nullable=False, index=True)
    notes = Column(String, default="")
    row_update_time = Column(DateTime)

    total_amount_seller_sold = Column(Float, default=0.0)
    total_quantity_seller_sold = Column(Integer, default=0)
    total_amount_member_sold = Column(Float, default=0.0)
    total_quantity_member_sold = Column(Integer, default=0)

    items = relationship("Item", back_populates="category")


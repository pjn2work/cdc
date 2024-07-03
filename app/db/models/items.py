from sqlalchemy import Column, Integer, Float, String, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship

from ..database import Base


class Categories(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    name = Column(String, index=True)
    notes = Column(String, default="")
    row_update_time = Column(DateTime)

    items = relationship("Items", back_populates="categories")


class Items(Base):
    __tablename__ = "items"
    __table_args__ = (UniqueConstraint("category_id", "name", name="uix_2"), )
    item_id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    category_id = Column(String, ForeignKey("categories.category_id"), index=True)

    name = Column(String, index=True)
    base_price = Column(Float)
    notes = Column(String, default="")
    row_update_time = Column(DateTime)

    categories = relationship("Categories", back_populates="items")
    seller_items = relationship("SellerItems", back_populates="items")
    member_items = relationship("MemberItems", back_populates="items")

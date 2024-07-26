from sqlalchemy import Column, Integer, Float, String, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship

from app.db.database import Base


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (UniqueConstraint("category_id", "name", name="uix_2"), )
    item_id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    category_id = Column(Integer, ForeignKey(column="categories.category_id", onupdate="CASCADE", ondelete="CASCADE"), index=True)

    name = Column(String, nullable=False, index=True)
    base_price = Column(Float)
    notes = Column(String, default="")
    row_update_time = Column(DateTime)

    total_amount_seller_sold = Column(Float, default=0.0)
    total_quantity_seller_sold = Column(Integer, default=0)
    total_amount_member_sold = Column(Float, default=0.0)
    total_quantity_member_sold = Column(Integer, default=0)

    category = relationship("Category", back_populates="items")
    seller_items = relationship("SellerItems", back_populates="item")
    member_items = relationship("MemberItems", back_populates="item")

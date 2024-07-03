from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class Sellers(Base):
    __tablename__ = "sellers"
    seller_id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    name = Column(String, index=True)
    tlf = Column(String)
    email = Column(String, default="")
    notes = Column(String, default="")

    seller_items = relationship("SellerItems", back_populates="sellers")
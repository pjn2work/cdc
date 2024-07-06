from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship

from app.db.database import Base


class DuesPayment(Base):
    __tablename__ = "dues_payments"
    id_year_month = Column(String, primary_key=True, index=True)

    date_ym = Column(Date, unique=True, index=True)
    year = Column(Integer, index=True)
    month = Column(Integer, index=True)

    member_due_payment = relationship("MemberDuesPayment", back_populates="dues_payment")

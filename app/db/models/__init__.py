import os

from app.db import get_db
from app.db.models.categories import Category
from app.db.models.dues_payments import DuesPayment
from app.db.models.expense_accounts import ExpenseAccount
from app.db.models.items import Item
from app.db.models.member_donations import MemberDonation
from app.db.models.member_due_payment import MemberDuesPayment
from app.db.models.member_items import MemberItems
from app.db.models.members import Member, MemberHistory
from app.db.models.seller_items import SellerItems
from app.db.models.sellers import Seller


def clear_db() -> None:
    if os.getenv("CDC_MODE") == "TEST":
        _db = next(get_db())
        try:
            _db.query(MemberDonation).delete()
            _db.query(MemberDuesPayment).delete()
            _db.query(MemberHistory).delete()

            _db.query(SellerItems).delete()
            _db.query(MemberItems).delete()
            _db.query(Item).delete()

            _db.query(DuesPayment).delete()
            _db.query(Category).delete()
            _db.query(ExpenseAccount).delete()
            _db.query(Seller).delete()
            _db.query(Member).delete()
            _db.commit()
        except:
            _db.rollback()

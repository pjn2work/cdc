from typing import List

from sqlalchemy.orm import Session

from app.db import models, schemas


def create_seller(db: Session, seller_create: schemas.sellers.SellerCreate) -> models.Seller:
    return None


def get_sellers_list(db: Session, skip: int, limit: int, search_text: str) -> List[models.Seller]:
    return None


def get_seller(db: Session, seller_id: int) -> models.Seller:
    return None


def get_seller_by_id(db: Session, seller_id: int) -> models.Seller:
    return None


def update_seller(db: Session, db_seller: models.Seller, seller_update: schemas.sellers.SellerUpdate) -> models.Seller:
    return None


# ----------------------------------------------------------


def create_expense_account(db: Session, expense_account_create: schemas.sellers.ExpenseAccountCreate) -> models.ExpenseAccount:
    return None


def get_expense_accounts_list(db: Session, skip: int, limit: int, search_text: str) -> List[models.ExpenseAccount]:
    return None


def get_expense_account(db: Session, ea_id: int) -> models.ExpenseAccount:
    return None


def get_expense_account_by_id(db: Session, ea_id: int) -> models.ExpenseAccount:
    return None


def update_expense_account(db: Session, db_expense_account: models.ExpenseAccount, expense_account_update: schemas.sellers.ExpenseAccountUpdate) -> models.ExpenseAccount:
    return None

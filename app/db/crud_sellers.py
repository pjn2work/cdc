from typing import List, Tuple

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db import models, schemas
from app.utils import get_now


def create_seller(db: Session, seller_create: schemas.sellers.SellerCreate) -> models.Seller:
    db_seller = models.Seller(**seller_create.model_dump())
    db_seller.row_update_time = get_now()
    try:
        db.add(db_seller)
        db.commit()
        db.refresh(db_seller)
    except:
        db.rollback()
        raise

    return db_seller


def get_sellers_list(db: Session, skip: int = 0, limit: int = 1000, search_text: str = None) -> List[models.Seller]:
    _dbq = db.query(models.Seller)

    if search_text is not None:
        _dbq = _dbq.filter(or_(
            models.Seller.name.ilike(f"%{search_text}%"),
            models.Seller.tlf.ilike(f"%{search_text}%"),
            models.Seller.email.ilike(f"%{search_text}%"),
            models.Seller.notes.ilike(f"%{search_text}%"),
        ))

    return _dbq.offset(skip).limit(limit).all()


def _get_seller_stats(db: Session, seller_id: int) -> Tuple[int, float]:
    _results = db.query(
        models.SellerItems
    ).filter_by(
        seller_id=seller_id
    ).order_by(models.SellerItems.sell_date).all()

    total_quantity_sold: int = sum([row.quantity for row in _results])
    total_amount_sold: float = sum([row.total_price for row in _results])

    return total_quantity_sold, total_amount_sold


def get_seller_by_id(db: Session, seller_id: int) -> models.Seller:
    db_seller = db.get(models.Seller, seller_id)
    if db_seller is None:
        raise HTTPException(status_code=404, detail=f"Seller {seller_id} not found")
    return db_seller


def get_seller(db: Session, seller_id: int) -> models.Seller:
    seller = get_seller_by_id(db, seller_id)

    seller.total_quantity_sold, seller.total_amount_sold = _get_seller_stats(db, seller_id)

    return seller


def update_seller(db: Session, db_seller: models.Seller, seller_update: schemas.sellers.SellerUpdate) -> models.Seller:
    db_seller.row_update_time = get_now()
    update_data = seller_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_seller, key, value)

    try:
        db.add(db_seller)
        db.commit()
        db.refresh(db_seller)
    except:
        db.rollback()
        raise

    return db_seller



# ----------------------------------------------------------


def create_expense_account(db: Session, expense_account_create: schemas.sellers.ExpenseAccountCreate) -> models.ExpenseAccount:
    db_expense_account = models.ExpenseAccount(**expense_account_create.model_dump())
    db_expense_account.row_update_time = get_now()
    try:
        db.add(db_expense_account)
        db.commit()
        db.refresh(db_expense_account)
    except:
        db.rollback()
        raise

    return db_expense_account


def get_expense_accounts_list(db: Session, skip: int, limit: int, search_text: str) -> List[models.ExpenseAccount]:
    _dbq = db.query(models.ExpenseAccount)

    if search_text is not None:
        _dbq = _dbq.filter(or_(
            models.ExpenseAccount.name.ilike(f"%{search_text}%"),
            models.ExpenseAccount.notes.ilike(f"%{search_text}%"),
        ))

    return _dbq.offset(skip).limit(limit).all()


def _get_expense_account_stats(db: Session, ea_id: int) -> Tuple[int, float]:
    _results = db.query(
        models.SellerItems
    ).filter_by(
        ea_id=ea_id
    ).all()

    total_quantity_seller_sold: int = sum([row.quantity for row in _results])
    total_amount_seller_sold: float = sum([row.total_price for row in _results])

    return total_quantity_seller_sold, total_amount_seller_sold


def get_expense_account_by_id(db: Session, ea_id: int) -> models.ExpenseAccount:
    db_expense_account = db.get(models.ExpenseAccount, ea_id)
    if db_expense_account is None:
        raise HTTPException(status_code=404, detail=f"Expense Account {ea_id} not found")
    return db_expense_account


def get_expense_account(db: Session, ea_id: int) -> models.ExpenseAccount:
    expense_account = get_expense_account_by_id(db, ea_id)

    expense_account.total_quantity_seller_sold, expense_account.total_amount_seller_sold = _get_expense_account_stats(db, ea_id)

    return expense_account


def update_expense_account(db: Session, db_expense_account: models.ExpenseAccount, expense_account_update: schemas.sellers.ExpenseAccountUpdate) -> models.ExpenseAccount:
    db_expense_account.row_update_time = get_now()
    update_data = expense_account_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_expense_account, key, value)

    try:
        db.add(db_expense_account)
        db.commit()
        db.refresh(db_expense_account)
    except:
        db.rollback()
        raise

    return db_expense_account
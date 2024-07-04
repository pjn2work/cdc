from typing import List

from fastapi import APIRouter
from sqlalchemy.orm import Session
from starlette import status

from ..db import crud_sellers, schemas, DB_SESSION

router = APIRouter()


@router.post(
    path="/",
    response_model=schemas.sellers.SellerView,
    status_code=status.HTTP_201_CREATED
)
def create_seller(
        seller_create: schemas.sellers.SellerCreate,
        db: Session = DB_SESSION):
    return crud_sellers.create_seller(db=db, seller_create=seller_create)


@router.get(
    path="/",
    response_model=List[schemas.sellers.Seller],
    status_code=status.HTTP_200_OK
)
def list_sellers(skip: int = 0, limit: int = 1000,
                 search_text: str = "",
                 db: Session = DB_SESSION):
    return crud_sellers.get_sellers_list(db, skip=skip, limit=limit, search_text=search_text)


@router.get(
    path="/{seller_id}",
    response_model=schemas.sellers.SellerView,
    status_code=status.HTTP_200_OK
)
def get_seller(seller_id: int, db: Session = DB_SESSION):
    return crud_sellers.get_seller(db, seller_id=seller_id)


@router.put(
    path="/{seller_id}",
    response_model=schemas.sellers.SellerView,
    status_code = status.HTTP_200_OK
)
def update_seller(seller_id: int,
                  seller_update: schemas.sellers.SellerUpdate,
                  db: Session = DB_SESSION):
    db_seller = crud_sellers.get_seller_by_id(db, seller_id=seller_id)
    return crud_sellers.update_seller(db, db_seller=db_seller, seller_update=seller_update)


# ----------------------------------------------------------


@router.post(
    path="/expense-accounts",
    response_model=schemas.sellers.ExpenseAccountView,
    status_code=status.HTTP_201_CREATED
)
def create_expense_account(
        expense_account_create: schemas.sellers.ExpenseAccountCreate,
        db: Session = DB_SESSION):
    return crud_sellers.create_expense_account(db=db, expense_account_create=expense_account_create)


@router.get(
    path="/expense-accounts",
    response_model=List[schemas.sellers.ExpenseAccount],
    status_code=status.HTTP_200_OK
)
def list_expense_accounts(skip: int = 0, limit: int = 1000,
                 search_text: str = "",
                 db: Session = DB_SESSION):
    return crud_sellers.get_expense_accounts_list(db, skip=skip, limit=limit, search_text=search_text)


@router.get(
    path="/expense-accounts/{ea_id}",
    response_model=schemas.sellers.ExpenseAccountView,
    status_code=status.HTTP_200_OK
)
def get_expense_account(ea_id: int, db: Session = DB_SESSION):
    return crud_sellers.get_expense_account(db, ea_id=ea_id)


@router.put(
    path="/expense-accounts/{ea_id}",
    response_model=schemas.sellers.ExpenseAccountView,
    status_code = status.HTTP_200_OK
)
def update_expense_account(ea_id: int,
                  expense_account_update: schemas.sellers.ExpenseAccountUpdate,
                  db: Session = DB_SESSION):
    db_expense_account = crud_sellers.get_expense_account_by_id(db, ea_id=ea_id)
    return crud_sellers.update_expense_account(db, db_seller=db_expense_account, expense_account_update=expense_account_update)

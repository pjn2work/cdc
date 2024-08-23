from typing import List

from fastapi import APIRouter
from sqlalchemy.orm import Session
from starlette import status

from app.api import error_json
from app.db import crud_sellers, schemas, DB_SESSION
from app.sec import GET_CURRENT_API_CLIENT, TokenData, are_valid_scopes
from app.utils.errors import CustomException

router = APIRouter()


@router.post(
    path="/expense-accounts",
    response_model=schemas.ExpenseAccountView,
    status_code=status.HTTP_201_CREATED
)
def create_expense_account(
        expense_account_create: schemas.ExpenseAccountCreate,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:create", "expense_account:create"], current_client)
    return crud_sellers.create_expense_account(db=db, expense_account_create=expense_account_create)


@router.get(
    path="/expense-accounts",
    response_model=List[schemas.ExpenseAccount],
    status_code=status.HTTP_200_OK
)
def list_expense_accounts(
        skip: int = 0, limit: int = 1000,
        search_text: str = "",
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:read", "expense_account:read"], current_client)

    try:
        return crud_sellers.get_expense_accounts_list(db, skip=skip, limit=limit, search_text=search_text)
    except CustomException as exc:
        return error_json(exc)


@router.get(
    path="/expense-accounts/{ea_id}",
    response_model=schemas.ExpenseAccountView,
    status_code=status.HTTP_200_OK
)
def get_expense_account(
        ea_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:read", "expense_account:read"], current_client)

    try:
        return crud_sellers.get_expense_account(db, ea_id=ea_id)
    except CustomException as exc:
        return error_json(exc)


@router.put(
    path="/expense-accounts/{ea_id}",
    response_model=schemas.ExpenseAccountView,
    status_code = status.HTTP_200_OK
)
def update_expense_account(
        ea_id: int,
        expense_account_update: schemas.ExpenseAccountUpdate,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:update", "expense_account:update"], current_client)

    try:
        db_expense_account = crud_sellers.get_expense_account_by_id(db, ea_id=ea_id)
        return crud_sellers.update_expense_account(db, db_expense_account=db_expense_account, expense_account_update=expense_account_update)
    except CustomException as exc:
        return error_json(exc)


# ----------------------------------------------------------


@router.post(
    path="/",
    response_model=schemas.SellerView,
    status_code=status.HTTP_201_CREATED
)
def create_seller(
        seller_create: schemas.SellerCreate,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:create", "seller:create"], current_client)
    return crud_sellers.create_seller(db=db, seller_create=seller_create)


@router.get(
    path="/",
    response_model=List[schemas.Seller],
    status_code=status.HTTP_200_OK
)
def list_sellers(
        skip: int = 0, limit: int = 1000,
        search_text: str = "",
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:read", "seller:read"], current_client)

    try:
        return crud_sellers.get_sellers_list(db, skip=skip, limit=limit, search_text=search_text)
    except CustomException as exc:
        return error_json(exc)


@router.get(
    path="/{seller_id}",
    response_model=schemas.SellerView,
    status_code=status.HTTP_200_OK
)
def get_seller(
        seller_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:read", "seller:read"], current_client)

    try:
        return crud_sellers.get_seller(db, seller_id=seller_id)
    except CustomException as exc:
        return error_json(exc)


@router.put(
    path="/{seller_id}",
    response_model=schemas.SellerView,
    status_code = status.HTTP_200_OK
)
def update_seller(
        seller_id: int,
        seller_update: schemas.SellerUpdate,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:update", "seller:update"], current_client)

    try:
        db_seller = crud_sellers.get_seller_by_id(db, seller_id=seller_id)
        return crud_sellers.update_seller(db, db_seller=db_seller, seller_update=seller_update)
    except CustomException as exc:
        return error_json(exc)

from typing import List

from fastapi import APIRouter
from sqlalchemy.orm import Session
from starlette import status

from app.api import error_json
from app.db import crud_dues_payments, schemas, DB_SESSION
from app.sec import GET_CURRENT_API_CLIENT, TokenData, are_valid_scopes
from app.utils.errors import CustomException

router = APIRouter()


@router.post(
    path="/",
    response_model=schemas.DuesPaymentView,
    status_code=status.HTTP_201_CREATED
)
def create_dues_payment_year_month(
        dues_payment_create: schemas.DuesPaymentCreate,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:create", "due_payment:create"], current_client)

    try:
        return crud_dues_payments.create_dues_payment_year_month(db=db, dues_payment_create=dues_payment_create)
    except CustomException as exc:
        return error_json(exc)


@router.get(
    path="/",
    response_model=List[schemas.DuesPaymentStats],
    status_code=status.HTTP_200_OK
)
def list_dues_payment_year_month_stats(
        since: str = None, until: str = None,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:read", "due_payment:read"], current_client)
    return crud_dues_payments.get_dues_payment_year_month_stats_list(db=db, since=since, until=until)


@router.get(
    path="/{id_year_month}/show",
    response_model=schemas.DuesPaymentView,
    status_code=status.HTTP_200_OK
)
def get_dues_payment_year_month_stats(
        id_year_month: str,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:read", "due_payment:read"], current_client)

    try:
        return crud_dues_payments.get_due_payment_year_month_stats(db=db, id_year_month=id_year_month)
    except CustomException as exc:
        return error_json(exc)

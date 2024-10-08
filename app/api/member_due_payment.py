from fastapi import APIRouter
from sqlalchemy.orm import Session
from starlette import status

from app.api import error_json
from app.db import crud_dues_payments, schemas, DB_SESSION
from app.sec import GET_CURRENT_API_CLIENT, TokenData, are_valid_scopes
from app.utils.errors import CustomException

router = APIRouter()


@router.get(
    path="/{tid}",
    response_model=schemas.MemberDuesPayment,
    status_code=status.HTTP_200_OK
)
def get_member_due_payment(
        tid: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:read", "member_due_payment:read"], current_client)

    try:
        return crud_dues_payments.get_member_due_payment(db, tid=tid)
    except CustomException as exc:
        return error_json(exc)


@router.put(
    path="/{tid}",
    response_model=schemas.MemberDuesPayment,
    status_code=status.HTTP_200_OK
)
def pay_member_due_payment(
        tid: int,
        mdpc: schemas.MemberDuesPaymentCreate,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:update", "member_due_payment:update"], current_client)

    try:
        return crud_dues_payments.pay_member_due_payment(db, tid=tid, mdpc=mdpc)
    except CustomException as exc:
        return error_json(exc)

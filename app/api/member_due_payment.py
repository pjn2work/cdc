from fastapi import APIRouter
from sqlalchemy.orm import Session
from starlette import status

from ..db import crud_dues_payments, schemas, DB_SESSION
from ..sec import GET_CURRENT_API_CLIENT, TokenData

router = APIRouter()


@router.get(
    path="/{tid}",
    response_model=schemas.member_due_payment.MemberDuesPayment,
    status_code=status.HTTP_200_OK
)
def get_member_due_payment(
        tid: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    return crud_dues_payments.get_member_due_payment(db, tid=tid)


@router.put(
    path="/{tid}",
    response_model=schemas.member_due_payment.MemberDuesPayment,
    status_code=status.HTTP_200_OK
)
def pay_member_due_payment(
        tid: int,
        mdpc: schemas.member_due_payment.MemberDuesPaymentCreate,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    return crud_dues_payments.pay_member_due_payment(db, tid=tid, mdpc=mdpc)

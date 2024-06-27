from fastapi import APIRouter
from sqlalchemy.orm import Session
from starlette import status

from ..db import crud, schemas, DB_SESSION


router = APIRouter()


@router.get(
    path="/{tid}",
    response_model=schemas.member_due_payment.MemberDuesPayment,
    status_code=status.HTTP_200_OK
)
def get_member_due_payment(tid: int, db: Session = DB_SESSION):
    return crud.get_member_due_payment(db, tid=tid)


@router.put(
    path="/{tid}",
    response_model=schemas.member_due_payment.MemberDuesPayment,
    status_code=status.HTTP_200_OK
)
def pay_member_due_payment(tid: int, db: Session = DB_SESSION):
    return crud.pay_member_due_payment(db, tid=tid)

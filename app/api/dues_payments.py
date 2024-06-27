from typing import List
from fastapi import APIRouter
from sqlalchemy.orm import Session
from starlette import status

from ..db import crud, schemas, DB_SESSION

router = APIRouter()


@router.post(
    path="/",
    response_model=schemas.dues_payments.DuesPayment,
    status_code=status.HTTP_201_CREATED
)
def create_dues_payment_year_month(dues_payment: schemas.dues_payments.DuesPaymentCreate,
                                   db: Session = DB_SESSION):
    return crud.create_dues_payment_year_month(db=db, dues_payment=dues_payment)


@router.get(
    path="/",
    response_model=List[schemas.dues_payments.DuesPaymentStats],
    status_code=status.HTTP_200_OK
)
def list_dues_payment_year_month_stats(since: str = None,
                                       until: str = None,
                                       db: Session = DB_SESSION):
    return crud.get_dues_payment_year_month_stats_list(db=db, since=since, until=until)


@router.get(
    path="/{id_year_month}/show",
    response_model=schemas.dues_payments.DuesPaymentStats,
    status_code=status.HTTP_200_OK
)
def get_dues_payment_year_month_stats(id_year_month: str, db: Session = DB_SESSION):
    return crud.get_due_payment_year_month_stats(db=db, id_year_month=id_year_month)

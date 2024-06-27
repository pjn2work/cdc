from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse

from . import templates
from ..db import crud, schemas, DB_SESSION
from ..utils import get_today_year_month_str

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def list_dues_payments(request: Request,
                       since: str = None,
                       until: str = None,
                       db: Session = DB_SESSION):
    dp_list = crud.get_dues_payment_year_month_stats_list(db, since=since, until=until)
    return templates.TemplateResponse("dues_payments_list.html", {
        "request": request,
        "dues_payments_list": dp_list,
        "total_results": len(dp_list),
        "since": since, "until": until,
        "this_month": get_today_year_month_str()
    })


@router.get("/{id_year_month}/show", response_class=HTMLResponse)
def get_due_payment(request: Request, id_year_month: str, db: Session = DB_SESSION):
    dp = crud.get_due_payment_year_month_stats(db, id_year_month=id_year_month)
    return templates.TemplateResponse("dues_payments_show.html", {
        "request": request,
        "dp": dp
    })


@router.post("/create", response_class=HTMLResponse)
async def create_due_payment_submit(request: Request, db: Session = DB_SESSION):
    data = await request.form()
    dues_payment: schemas.dues_payments.DuesPaymentCreate = schemas.dues_payments.DuesPaymentCreate(**data)

    dp = crud.create_dues_payment_year_month(db=db, dues_payment=dues_payment)
    return RedirectResponse(url=f"{dp.id_year_month}/show", status_code=303)

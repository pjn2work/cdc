from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse

from app.db import crud_dues_payments, schemas, DB_SESSION
from app.sec import GET_CURRENT_WEB_CLIENT, TokenData, are_valid_scopes
from app.utils import get_today_year_month_str, get_today
from app.utils.errors import CustomException
from app.web import templates, error_page

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def list_dues_payments(
        request: Request,
        since: str = None, until: str = None,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "due_payment:read"], current_client)

    try:
        dp_list = crud_dues_payments.get_dues_payment_year_month_stats_list(db, since=since, until=until)
    except CustomException as exc:
        return error_page(request, exc)

    return templates.TemplateResponse("due_payments/dues_payments_list.html", {
        "request": request,
        "dues_payments_list": dp_list,
        "total_results": len(dp_list),
        "since": since, "until": until,
        "this_month": get_today_year_month_str()
    })


@router.get("/{id_year_month}/show", response_class=HTMLResponse)
def get_due_payment(
        request: Request,
        id_year_month: str,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "due_payment:read"], current_client)

    try:
        dp = crud_dues_payments.get_due_payment_year_month_stats(db, id_year_month=id_year_month)
    except CustomException as exc:
        return error_page(request, exc)

    return templates.TemplateResponse("due_payments/dues_payments_show.html", {
        "request": request,
        "dp": dp,
        "today": get_today()
    })


@router.post("/create", response_class=HTMLResponse)
async def create_due_payment_submit(
        request: Request,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "due_payment:create"], current_client)

    data = await request.form()
    dues_payment_create: schemas.DuesPaymentCreate = schemas.DuesPaymentCreate(**data)

    try:
        dp = crud_dues_payments.create_dues_payment_year_month(db=db, dues_payment_create=dues_payment_create)
    except CustomException as exc:
        return error_page(request, exc)

    return RedirectResponse(url=f"{dp.id_year_month}/show", status_code=303)

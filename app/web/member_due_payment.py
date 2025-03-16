from fastapi import APIRouter, Request
from pydantic_core import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse

from app.db import crud_dues_payments, schemas, DB_SESSION
from app.sec import GET_CURRENT_WEB_CLIENT, TokenData, are_valid_scopes
from app.utils.errors import CustomException
from app.web import templates, error_page

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def list_member_dues_payments_order_by_pay_date(
        request: Request,
        since: str = None,
        until: str = None,
        just_download: bool = False,
        do_filter: bool = False,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "member_due_payment:read"], current_client)

    if do_filter:
        mdp_list = crud_dues_payments.list_member_dues_payments_order_by_pay_date(db, since=since, until=until, just_download=just_download)

        if just_download:
            return mdp_list
    else:
        mdp_list = []

    return templates.TemplateResponse(request=request, name="due_payments/member_due_payment_list.html", context={
        "mdp_list": mdp_list,
        "total": len(mdp_list),
    })


@router.post("/{tid}", response_class=HTMLResponse)
async def pay_member_due_payment(
        request: Request,
        tid: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "member_due_payment:create"], current_client)

    data = await request.form()

    try:
        mdpc: schemas.MemberDuesPaymentCreate = schemas.MemberDuesPaymentCreate(**data)

        mdp = crud_dues_payments.pay_member_due_payment(db, tid=tid, mdpc=mdpc)
    except (CustomException, ValidationError) as exc:
        return error_page(request, exc)

    #return RedirectResponse(url=f"../members/{mdp.member_id}/show", status_code=303)
    referer = request.headers.get("Referer")
    return RedirectResponse(url=referer, status_code=303)


@router.get("/pivot_table", response_class=HTMLResponse)
def table_dues_paid_for_all_members(
        request: Request,
        since: str = None,
        until: str = None,
        just_download: bool = False,
        do_filter: bool = False,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "member_due_payment:read"], current_client)

    if do_filter:
        result = crud_dues_payments.pivot_table_dues_paid_for_all_members(db, since=since, until=until, just_download=just_download)

        if just_download:
            return result

        df_paid, df_missing = result
        columns = [
            col
            for col in df_paid.columns
            if col not in ("ID", "Nome")
        ]
        df_paid = df_paid.to_dict(orient="records")
        df_missing = df_missing.to_dict(orient="records")
    else:
        df_paid, df_missing = [{}], [{}]
        columns = []

    return templates.TemplateResponse(request=request, name="due_payments/member_due_payment_pivot.html", context={
        "columns": columns,
        "df_paid": df_paid,
        "df_missing": df_missing
    })

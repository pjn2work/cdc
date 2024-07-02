from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse

from . import templates
from ..db import crud_dues_payments, schemas, DB_SESSION


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def list_member_dues_payments_order_by_pay_date(
        request: Request,
        since: str = None,
        until: str = None,
        just_download: bool = False,
        do_filter: bool = False,
        db: Session = DB_SESSION):

    if do_filter:
        mdp_list = crud_dues_payments.list_member_dues_payments_order_by_pay_date(db, since=since, until=until, just_download=just_download)

        if just_download:
            return mdp_list
    else:
        mdp_list = []

    return templates.TemplateResponse("member_due_payment_list.html", {
        "request": request,
        "mdp_list": mdp_list,
        "total": len(mdp_list),
    })


@router.post("/{tid}", response_class=HTMLResponse)
async def pay_member_due_payment(
        request: Request,
        tid: int,
        db: Session = DB_SESSION):
    data = await request.form()
    mdpc: schemas.member_due_payment.MemberDuesPaymentCreate = schemas.member_due_payment.MemberDuesPaymentCreate(**data)

    mdp = crud_dues_payments.pay_member_due_payment(db, tid=tid, mdpc=mdpc)
    return RedirectResponse(url=f"../members/{mdp.member_id}/show", status_code=303)


@router.get("/pivot_table", response_class=HTMLResponse)
def table_dues_paied_for_all_members(
        request: Request,
        since: str = None,
        until: str = None,
        just_download: bool = False,
        do_filter: bool = False,
        db: Session = DB_SESSION):

    if do_filter:
        result = crud_dues_payments.pivot_table_dues_paied_for_all_members(db, since=since, until=until, just_download=just_download)

        if just_download:
            return result

        df_paied, df_missing = result
        columns = [
            col
            for col in df_paied.columns
            if col not in ("ID", "Nome")
        ]
        df_paied = df_paied.to_dict(orient="records")
        df_missing = df_missing.to_dict(orient="records")
    else:
        df_paied, df_missing = [{}], [{}]
        columns = []

    return templates.TemplateResponse("member_due_payment_pivot.html", {
        "request": request,
        "columns": columns,
        "df_paied": df_paied,
        "df_missing": df_missing
    })

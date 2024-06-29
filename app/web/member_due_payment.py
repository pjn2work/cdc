from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse

from . import templates
from ..db import crud, DB_SESSION


router = APIRouter()


@router.post("/{tid}", response_class=HTMLResponse)
def pay_member_due_payment(tid: int, db: Session = DB_SESSION):
    mdp = crud.pay_member_due_payment(db, tid=tid)
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
        df_paied, df_missing, excel_file = crud.pivot_table_dues_paied_for_all_members(db, since=since, until=until)

        if just_download:
            return excel_file

        columns = [
            col
            for col in df_paied.columns
            if col not in ("member_id", "name", "total")
        ]
        df_paied = df_paied.to_dict(orient="records")
        df_missing = df_missing.to_dict(orient="records")
    else:
        df_paied, df_missing, excel_file = [{}], [{}], None
        columns = []

    return templates.TemplateResponse("member_due_payment_pivot.html", {
        "request": request,
        "columns": columns,
        "df_paied": df_paied,
        "df_missing": df_missing
    })

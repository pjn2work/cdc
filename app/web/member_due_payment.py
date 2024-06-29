from fastapi import APIRouter
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse

from ..db import crud, DB_SESSION


router = APIRouter()


@router.post("/{tid}", response_class=HTMLResponse)
def pay_member_due_payment(tid: int, db: Session = DB_SESSION):
    mdp = crud.pay_member_due_payment(db, tid=tid)
    return RedirectResponse(url=f"../members/{mdp.member_id}/show", status_code=303)


@router.get("/pivot_table", response_class=HTMLResponse)
def table_dues_paied_for_all_members(
                       since: str = None,
                       until: str = None,
                       db: Session = DB_SESSION):
    excel_file = crud.pivot_table_dues_paied_for_all_members(db, since=since, until=until)
    return excel_file

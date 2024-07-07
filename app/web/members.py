from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse

from app.db import crud_member, schemas, DB_SESSION
from app.sec import GET_CURRENT_WEB_CLIENT, TokenData, are_valid_scopes
from app.utils import get_today_year_month_str, get_today
from app.web import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def list_members(
        request: Request,
        only_due_missing: bool = None,
        only_active_members: bool = None,
        search_text: str = "",
        do_filter: bool = False,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "member:read"], current_client)

    if do_filter:
        members = crud_member.get_members_list(db, only_due_missing=only_due_missing, only_active_members=only_active_members, search_text=search_text)
    else:
        members = []

    return templates.TemplateResponse("members_list.html", {
        "request": request,
        "members": members,
        "total_results": len(members)
    })


@router.get("/create", response_class=HTMLResponse)
def create_member(
        request: Request,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "member:create"], current_client)

    return templates.TemplateResponse("members_create.html", {
        "request": request,
        "today": str(get_today())
    })


@router.post("/create", response_class=HTMLResponse)
async def create_member_submit(
        request: Request,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "member:create"], current_client)

    data = await request.form()
    member_create: schemas.members.MemberCreate = schemas.members.MemberCreate(**data)

    member = crud_member.create_member(db=db, member_create=member_create)
    return RedirectResponse(url=f"{member.member_id}/show", status_code=303)


@router.get("/{member_id}/show", response_class=HTMLResponse)
def show_member(
        request: Request,
        member_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "member:read"], current_client)

    member = crud_member.get_member(db, member_id=member_id)
    member.member_due_payment = sorted(member.member_due_payment, key=lambda mdp: mdp.id_year_month, reverse=True)
    member.member_history = sorted(member.member_history, key=lambda mh: mh.tid, reverse=True)
    return templates.TemplateResponse("members_show.html", {
        "request": request,
        "member": member,
        "this_month": get_today_year_month_str(),
        "today": get_today()
    })


@router.post("/{member_id}/active", response_class=HTMLResponse)
async def change_member_active(
        request: Request,
        member_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "member:update"], current_client)

    data = await request.form()
    member_update: schemas.members.MemberUpdateActive = schemas.members.MemberUpdateActive(**data)

    db_member = crud_member.get_member_by_id(db, member_id=member_id)
    _ = crud_member.update_member_active(db, db_member=db_member, member_update=member_update)
    return RedirectResponse(url=f"show", status_code=303)


@router.post("/{member_id}/amount", response_class=HTMLResponse)
async def change_member_due_payment_amount(
        request: Request,
        member_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "member:update"], current_client)

    data = await request.form()
    member_update: schemas.members.MemberUpdateAmount = schemas.members.MemberUpdateAmount(**data)

    db_member = crud_member.get_member_by_id(db, member_id=member_id)
    _ = crud_member.update_member_amount(db, db_member=db_member, member_update=member_update)
    return RedirectResponse(url=f"show", status_code=303)


@router.get("/{member_id}/update", response_class=HTMLResponse)
def edit_member(
        request: Request,
        member_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "member:update"], current_client)

    member = crud_member.get_member(db, member_id=member_id)
    return templates.TemplateResponse("members_edit.html", {
        "request": request,
        "member": member
    })


@router.post("/{member_id}/update", response_class=HTMLResponse)
async def update_member(
        request: Request,
        member_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "member:update"], current_client)

    data = await request.form()
    member_update: schemas.members.MemberUpdate = schemas.members.MemberUpdate(**data)

    db_member = crud_member.get_member_by_id(db, member_id=member_id)
    _ = crud_member.update_member(db, db_member=db_member, member_update=member_update)
    return RedirectResponse(url=f"show", status_code=303)


@router.post("/{member_id}/donation", response_class=HTMLResponse)
async def post_member_donation(
        request: Request,
        member_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "member_donation:create"], current_client)

    data = await request.form()
    member_donation_create: schemas.member_donations.MemberDonationCreate = schemas.member_donations.MemberDonationCreate(**data)

    _ = crud_member.post_member_donation(db, member_id=member_id, member_donation_create=member_donation_create)
    return RedirectResponse(url=f"show", status_code=303)


@router.get("/donations", response_class=HTMLResponse)
async def list_members_donations(
        request: Request,
        since: str = None,
        until: str = None,
        just_download: bool = False,
        do_filter: bool = False,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "member_donation:read"], current_client)

    if do_filter:
        md_list = crud_member.list_member_donations_order_by_pay_date(db, since=since, until=until, just_download=just_download)

        if just_download:
            return md_list
    else:
        md_list = []

    return templates.TemplateResponse("member_donations_list.html", {
        "request": request,
        "md_list": md_list,
        "total": len(md_list),
    })

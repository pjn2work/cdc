from fastapi import APIRouter, Request, status
from pydantic_core import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse

from app.db import crud_member, schemas, DB_SESSION
from app.sec import GET_CURRENT_WEB_CLIENT, TokenData, are_valid_scopes
from app.utils import get_today_year_month_str, get_today
from app.utils.errors import CustomException
from app.web import templates, error_page

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

    return templates.TemplateResponse(request=request, name="members/members_list.html", context={
        "members": members,
        "total_results": len(members)
    })


@router.get("/create", response_class=HTMLResponse)
def create_member(
        request: Request,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "member:create"], current_client)

    return templates.TemplateResponse(request=request, name="members/members_create.html", context={"today": str(get_today())})


@router.post("/create", response_class=HTMLResponse)
async def create_member_submit(
        request: Request,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "member:create"], current_client)

    data = await request.form()

    try:
        member_create: schemas.MemberCreate = schemas.MemberCreate(**data)

        member = crud_member.create_member(db=db, member_create=member_create)
    except (CustomException, ValidationError) as exc:
        return error_page(request, exc)

    return RedirectResponse(url=f"{member.member_id}/show", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{member_id}/show", response_class=HTMLResponse)
def show_member(
        request: Request,
        member_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "member:read"], current_client)

    try:
        member = crud_member.get_member(db, member_id=member_id)
    except CustomException as exc:
        return error_page(request, exc)

    return templates.TemplateResponse(request=request, name="members/members_show.html", context={
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

    try:
        member_update: schemas.MemberUpdateActive = schemas.MemberUpdateActive(**data)

        db_member = crud_member.get_member_by_id(db, member_id=member_id)
        _ = crud_member.update_member_active(db, db_member=db_member, member_update=member_update)
    except (CustomException, ValidationError) as exc:
        return error_page(request, exc)

    return RedirectResponse(url=f"show", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{member_id}/amount", response_class=HTMLResponse)
async def change_member_due_payment_amount(
        request: Request,
        member_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "member:update"], current_client)

    data = await request.form()

    try:
        member_update: schemas.MemberUpdateAmount = schemas.MemberUpdateAmount(**data)

        db_member = crud_member.get_member_by_id(db, member_id=member_id)
        _ = crud_member.update_member_amount(db, db_member=db_member, member_update=member_update)
    except (CustomException, ValidationError) as exc:
        return error_page(request, exc)

    return RedirectResponse(url=f"show", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{member_id}/update", response_class=HTMLResponse)
def edit_member(
        request: Request,
        member_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "member:update"], current_client)

    try:
        member = crud_member.get_member(db, member_id=member_id)
    except CustomException as exc:
        return error_page(request, exc)

    return templates.TemplateResponse(request=request, name="members/members_edit.html", context={"member": member})


@router.post("/{member_id}/update", response_class=HTMLResponse)
async def update_member(
        request: Request,
        member_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "member:update"], current_client)

    data = await request.form()

    try:
        member_update: schemas.MemberUpdate = schemas.MemberUpdate(**data)

        db_member = crud_member.get_member_by_id(db, member_id=member_id)
        _ = crud_member.update_member(db, db_member=db_member, member_update=member_update)
    except (CustomException, ValidationError) as exc:
        return error_page(request, exc)

    return RedirectResponse(url=f"show", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{member_id}/donation", response_class=HTMLResponse)
async def post_member_donation(
        request: Request,
        member_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "member_donation:create"], current_client)

    data = await request.form()

    try:
        member_donation_create: schemas.MemberDonationCreate = schemas.MemberDonationCreate(**data)

        _ = crud_member.post_member_donation(db, member_id=member_id, member_donation_create=member_donation_create)
    except (CustomException, ValidationError) as exc:
        return error_page(request, exc)

    return RedirectResponse(url=f"show", status_code=status.HTTP_303_SEE_OTHER)


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

    return templates.TemplateResponse(request=request, name="due_payments/member_donations_list.html", context={
        "md_list": md_list,
        "total": len(md_list),
    })

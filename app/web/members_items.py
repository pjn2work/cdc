from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse

from app.db import crud_items, crud_member, schemas, DB_SESSION
from app.sec import GET_CURRENT_WEB_CLIENT, TokenData, are_valid_scopes
from app.utils import get_today
from app.web import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def list_members_items(
        request: Request,
        do_filter: bool = False,
        search_text: str = "",
        member_id: int = 0,
        item_id: int = 0,
        category_id: int = 0,
        tid: int = 0,
        since: str = "", until: str = "",
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "member_item:read"], current_client)

    if do_filter:
        members_items = crud_items.get_members_items_list(db, member_id=member_id, item_id=item_id, category_id=category_id, tid=tid, since=since, until=until, search_text=search_text)
    else:
        members_items = []

    categories = crud_items.get_categories_list(db, search_text="")
    items = crud_items.get_items_list(db, search_text="")
    members = crud_member.get_members_list(db, search_text="")

    return templates.TemplateResponse("items/member_item_list.html", {
        "request": request,
        "categories": categories,
        "items": items,
        "members": members,
        "members_items": members_items,
        "since": since,
        "until": until,
        "total_results": len(members_items)
    })


@router.get("/create", response_class=HTMLResponse)
def create_member_item(
        request: Request,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "member_item:create"], current_client)

    return templates.TemplateResponse("items/member_item_create.html", {
        "request": request,
        "today": str(get_today())
    })


@router.post("/create", response_class=HTMLResponse)
async def create_member_item_submit(
        request: Request,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "member_item:create"], current_client)

    data = await request.form()
    member_item_create: schemas.MemberItemsCreate = schemas.MemberItemsCreate(**data)

    member = crud_items.create_member_item(db=db, member_item_create=member_item_create)
    return RedirectResponse(url=f"{member.member_id}/show", status_code=303)


@router.get("/{tid}/update", response_class=HTMLResponse)
def edit_member_item(
        request: Request,
        tid: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "member_item:update"], current_client)

    member_item = crud_items.get_member_item(db, tid=tid)
    return templates.TemplateResponse("items/member_item_edit.html", {
        "request": request,
        "member_item": member_item
    })


@router.post("/{tid}/update", response_class=HTMLResponse)
async def update_member_item(
        request: Request,
        tid: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "member_item:update"], current_client)

    data = await request.form()
    member_item_update: schemas.MemberItemsUpdate = schemas.MemberItemsUpdate(**data)

    db_member_item = crud_items.get_member_item(db, tid=tid)
    _ = crud_items.update_member_item(db, db_member_item=db_member_item, member_item_update=member_item_update)
    return RedirectResponse(url=f"?tid={tid}", status_code=303)

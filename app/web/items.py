from typing import Optional

from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse

from app.db import crud_items, schemas, DB_SESSION
from app.sec import GET_CURRENT_WEB_CLIENT, TokenData, are_valid_scopes
from app.utils import get_today
from app.web import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def list_items(
        request: Request,
        do_filter: bool = False,
        search_text: str = "",
        category_id: Optional[str] = "",
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "item:read"], current_client)

    categories = crud_items.get_categories_list(db, search_text="")
    if do_filter:
        items = crud_items.get_items_list(db, search_text=search_text, category_id=category_id)
    else:
        items = []

    return templates.TemplateResponse("items/items_list.html", {
        "request": request,
        "items": items,
        "categories": categories,
        "total_results": len(items)
    })


@router.get("/create", response_class=HTMLResponse)
def create_item(
        request: Request,
        category_id: int,
        category_name: str,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "item:create"], current_client)

    return templates.TemplateResponse("items/items_create.html", {
        "request": request,
        "category_id": category_id,
        "category_name": category_name,
        "today": str(get_today())
    })


@router.post("/create", response_class=HTMLResponse)
async def create_item_submit(
        request: Request,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "item:create"], current_client)

    data = await request.form()
    item_create: schemas.ItemCreate = schemas.ItemCreate(**data)

    item = crud_items.create_item(db=db, item_create=item_create)
    return RedirectResponse(url=f"{item.item_id}/show", status_code=303)


@router.get("/{item_id}/show", response_class=HTMLResponse)
def show_item(
        request: Request,
        item_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "item:read"], current_client)

    item = crud_items.get_item(db, item_id=item_id)
    return templates.TemplateResponse("items/items_show.html", {
        "request": request,
        "item": item,
        "today": get_today()
    })


@router.get("/{item_id}/update", response_class=HTMLResponse)
def edit_item(
        request: Request,
        item_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "item:update"], current_client)

    item = crud_items.get_item(db, item_id=item_id)
    return templates.TemplateResponse("items/items_edit.html", {
        "request": request,
        "item": item
    })


@router.post("/{item_id}/update", response_class=HTMLResponse)
async def update_item(
        request: Request,
        item_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "item:update"], current_client)

    data = await request.form()
    item_update: schemas.ItemUpdate = schemas.ItemUpdate(**data)

    db_item = crud_items.get_item_by_id(db, item_id=item_id)
    _ = crud_items.update_item(db, db_item=db_item, item_update=item_update)
    return RedirectResponse(url=f"show", status_code=303)

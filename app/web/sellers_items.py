from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse

from app.db import crud_items, crud_sellers, schemas, DB_SESSION
from app.sec import GET_CURRENT_WEB_CLIENT, TokenData, are_valid_scopes
from app.utils import get_today
from app.web import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def list_seller_item(
        request: Request,
        do_filter: bool = False,
        search_text: str = "",
        seller_id: int = 0,
        ea_id: int = 0,
        item_id: int = 0,
        category_id: int = 0,
        tid: int = 0,
        since: str = "", until: str = "",
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "seller_item:read"], current_client)

    if do_filter:
        sellers_items = crud_items.get_sellers_items_list(db, seller_id=seller_id, ea_id=ea_id, item_id=item_id, category_id=category_id, tid=tid, since=since, until=until, search_text=search_text)
    else:
        sellers_items = []

    categories = crud_items.get_categories_list(db, search_text="")
    items = crud_items.get_items_list(db, search_text="")
    sellers = crud_sellers.get_sellers_list(db, search_text="")
    expense_accounts = crud_sellers.get_expense_accounts_list(db, search_text="")

    return templates.TemplateResponse("items/seller_item_list.html", {
        "request": request,
        "categories": categories,
        "items": items,
        "sellers": sellers,
        "expense_accounts": expense_accounts,
        "sellers_items": sellers_items,
        "since": since,
        "until": until,
        "seller_id": seller_id,
        "ea_id": ea_id,
        "item_id": item_id,
        "category_id": category_id,
        "search_text": search_text,
        "total_results": len(sellers_items)
    })


@router.get("/create", response_class=HTMLResponse)
def create_seller_item(
        request: Request,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "seller_item:create"], current_client)

    return templates.TemplateResponse("items/seller_item_create.html", {
        "request": request,
        "today": str(get_today())
    })


@router.post("/create", response_class=HTMLResponse)
async def create_seller_item_submit(
        request: Request,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "seller_item:create"], current_client)

    data = await request.form()
    seller_item_create: schemas.SellerItemsCreate = schemas.SellerItemsCreate(**data)

    seller = crud_items.create_seller_item(db=db, seller_item_create=seller_item_create)
    return RedirectResponse(url=f"{seller.seller_id}/show", status_code=303)


@router.get("/{tid}/update", response_class=HTMLResponse)
def edit_seller_item(
        request: Request,
        tid: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "seller_item:update"], current_client)

    seller_item = crud_items.get_seller_item(db, tid=tid)
    return templates.TemplateResponse("items/seller_item_edit.html", {
        "request": request,
        "seller_item": seller_item
    })


@router.post("/{tid}/update", response_class=HTMLResponse)
async def update_seller_item(
        request: Request,
        tid: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "seller_item:update"], current_client)

    data = await request.form()
    seller_item_update: schemas.SellerItemsUpdate = schemas.SellerItemsUpdate(**data)

    db_seller_item = crud_items.get_seller_item(db, tid=tid)
    _ = crud_items.update_seller_item(db, db_seller_item=db_seller_item, seller_item_update=seller_item_update)
    return RedirectResponse(url=f"?tid={tid}", status_code=303)

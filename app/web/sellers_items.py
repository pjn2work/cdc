from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse

from app.db import crud_items, crud_sellers, schemas, DB_SESSION
from app.sec import GET_CURRENT_WEB_CLIENT, TokenData, are_valid_scopes
from app.utils import get_today
from app.utils.errors import CustomException
from app.web import templates, error_page

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def list_sellers_items(
        request: Request,
        do_filter: bool = False,
        search_text: str = "",
        seller_id: int = 0,
        ea_id: int = 0,
        item_id: int = 0,
        category_id: int = 0,
        tid: int = 0,
        since: str = "", until: str = "",
        just_download: bool = False,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "seller_item:read"], current_client)

    if do_filter:
        sellers_items = crud_items.get_sellers_items_list(db, seller_id=seller_id, ea_id=ea_id, item_id=item_id, category_id=category_id, tid=tid, since=since, until=until, just_download=just_download, search_text=search_text)

        if just_download:
            return sellers_items
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
        item_id: int = 0,
        seller_id: int = 0,
        ea_id: int = 0,
        item_base_price: float = 0.0,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "seller_item:create"], current_client)

    items = crud_items.get_items_list(db, search_text="")
    sellers = crud_sellers.get_sellers_list(db, search_text="")
    expense_accounts = crud_sellers.get_expense_accounts_list(db, search_text="")

    return templates.TemplateResponse("items/seller_item_create.html", {
        "request": request,
        "item_id": item_id,
        "seller_id": seller_id,
        "ea_id": ea_id,
        "item_base_price": item_base_price,
        "items": items,
        "sellers": sellers,
        "expense_accounts": expense_accounts,
        "today": str(get_today())
    })


@router.post("/create", response_class=HTMLResponse)
async def create_seller_item_submit(
        request: Request,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "seller_item:create"], current_client)

    data = {**await request.form()}
    data["is_cash"] = data.get("is_cash", False)
    item_id = int(data["item_id"])
    del data["item_id"]

    seller_item_create: schemas.SellerItemsCreate = schemas.SellerItemsCreate(**data)

    try:
        seller_item = crud_items.create_seller_item(db=db, item_id=item_id, seller_item_create=seller_item_create)
    except CustomException as exc:
        return error_page(request, exc)

    return RedirectResponse(url=f"../sellers-items/?do_filter=on&tid={seller_item.tid}", status_code=303)


@router.get("/{tid}/update", response_class=HTMLResponse)
def edit_seller_item(
        request: Request,
        tid: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "seller_item:update"], current_client)

    try:
        seller_item = crud_items.get_seller_item(db, tid=tid)
    except CustomException as exc:
        return error_page(request, exc)

    items = crud_items.get_items_list(db, search_text="")
    sellers = crud_sellers.get_sellers_list(db, search_text="")
    expense_accounts = crud_sellers.get_expense_accounts_list(db, search_text="")

    return templates.TemplateResponse("items/seller_item_edit.html", {
        "request": request,
        "seller_item": seller_item,
        "items": items,
        "sellers": sellers,
        "expense_accounts": expense_accounts
    })


@router.post("/{tid}/update", response_class=HTMLResponse)
async def update_seller_item(
        request: Request,
        tid: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "seller_item:update"], current_client)

    data = {**await request.form()}
    if "is_cash" not in data:
        data["is_cash"] = False

    seller_item_update: schemas.SellerItemsUpdate = schemas.SellerItemsUpdate(**data)

    try:
        db_seller_item = crud_items.get_seller_item(db, tid=tid)
        _ = crud_items.update_seller_item(db, db_seller_item=db_seller_item, seller_item_update=seller_item_update)
    except CustomException as exc:
        return error_page(request, exc)

    return RedirectResponse(url=f"../../sellers-items/?do_filter=on&tid={tid}", status_code=303)

from fastapi import APIRouter, Request
from pydantic_core import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse

from app.db import crud_items, crud_member, schemas, DB_SESSION
from app.sec import GET_CURRENT_WEB_CLIENT, TokenData, are_valid_scopes
from app.utils import get_today
from app.utils.errors import CustomException
from app.web import templates, error_page, flash

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
        just_download: bool = False,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "member_item:read"], current_client)

    if do_filter:
        members_items = crud_items.get_members_items_list(db, member_id=member_id, item_id=item_id, category_id=category_id, tid=tid, since=since, until=until, just_download=just_download, search_text=search_text)

        if just_download:
            return members_items
    else:
        members_items = []

    categories = crud_items.get_categories_list(db, search_text="")
    items = crud_items.get_items_list(db, search_text="")
    members = crud_member.get_members_list(db, search_text="")

    return templates.TemplateResponse(request=request, name="items/member_item_list.html", context={
        "request": request,
        "categories": categories,
        "items": items,
        "members": members,
        "members_items": members_items,
        "since": since,
        "until": until,
        "member_id": member_id,
        "item_id": item_id,
        "category_id": category_id,
        "search_text": search_text,
        "total_results": len(members_items)
    })


@router.get("/create", response_class=HTMLResponse)
def create_member_item(
        request: Request,
        item_id: int = 0,
        member_id: int = 0,
        item_base_price: float = 0.0,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "member_item:create"], current_client)

    items = crud_items.get_items_list(db, search_text="")
    members = crud_member.get_members_list(db, search_text="")
    categories = crud_items.get_categories_list(db, search_text="")

    items_data = [{
        "item_id": item.item_id,
        "name": item.name,
        "base_price": item.base_price or 0,
        "category_id": item.category_id,
        "category_name": item.category.name if item.category else "",
    } for item in items]

    return templates.TemplateResponse(request=request, name="items/member_item_create.html", context={
        "item_id": item_id,
        "member_id": member_id,
        "items_data": items_data,
        "members": members,
        "categories": categories,
        "today": str(get_today())
    })


@router.post("/create")
async def create_member_item_submit(
        request: Request,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "member_item:create"], current_client)

    try:
        data = await request.json()
        member_id = int(data["member_id"])
        purchase_date = data["purchase_date"]
        is_cash = bool(data.get("is_cash", False))
        cart_items = data["items"]

        if not cart_items:
            raise CustomException("Nenhum item no carrinho.")

        created = []
        for ci in cart_items:
            mic = schemas.MemberItemsCreate(
                member_id=member_id,
                quantity=int(ci["quantity"]),
                total_price=float(ci["total_price"]),
                notes=ci.get("notes", ""),
                purchase_date=purchase_date,
                is_cash=is_cash,
            )
            mi = crud_items.create_member_item(db=db, item_id=int(ci["item_id"]), member_item_create=mic)
            created.append(mi)

        total_qty = sum(mi.quantity for mi in created)
        total_price = sum(mi.total_price for mi in created)
        member_name = created[0].member.name
        flash(request, f"Venda de {total_qty} items no valor de {total_price:.2f}€ ao associado {member_name} criada com sucesso.", "success")

        return JSONResponse({"redirect": f"../members-items/?do_filter=on&member_id={member_id}"})

    except (CustomException, ValidationError) as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)


@router.get("/{tid}/update", response_class=HTMLResponse)
def edit_member_item(
        request: Request,
        tid: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "member_item:update"], current_client)

    try:
        member_item = crud_items.get_member_item(db, tid=tid)
    except CustomException as exc:
        return error_page(request, exc)

    items = crud_items.get_items_list(db, search_text="")
    members = crud_member.get_members_list(db, search_text="")

    return templates.TemplateResponse(request=request, name="items/member_item_edit.html", context={
        "member_item": member_item,
        "items": items,
        "members": members,
    })


@router.post("/{tid}/delete", response_class=HTMLResponse)
async def delete_member_item(
        request: Request,
        tid: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:delete", "member_item:delete"], current_client)

    try:
        crud_items.delete_member_item(db, tid=tid)
        flash(request, f"Venda removida com sucesso.", "success")
    except CustomException as exc:
        return error_page(request, exc)

    referer = request.headers.get("Referer")
    return RedirectResponse(url=referer, status_code=303)


@router.post("/{tid}/update", response_class=HTMLResponse)
async def update_member_item(
        request: Request,
        tid: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "member_item:update"], current_client)

    data = {**await request.form()}
    if "is_cash" not in data:
        data["is_cash"] = False

    try:
        member_item_update: schemas.MemberItemsUpdate = schemas.MemberItemsUpdate(**data)

        db_member_item = crud_items.get_member_item(db, tid=tid)
        member_item = crud_items.update_member_item(db, db_member_item=db_member_item, member_item_update=member_item_update)
        flash(request, f"Actualização de compra de {member_item.quantity} items de '{member_item.item.name}' no valor de {member_item.total_price}€ ao associado {member_item.member.name} feita com sucesso.", "success")
    except (CustomException, ValidationError) as exc:
        return error_page(request, exc)

    return RedirectResponse(url=f"../../members-items/?do_filter=on&tid={tid}", status_code=303)

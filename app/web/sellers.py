from fastapi import APIRouter, Request
from pydantic_core import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse

from app.db import crud_sellers, schemas, DB_SESSION
from app.sec import GET_CURRENT_WEB_CLIENT, TokenData, are_valid_scopes
from app.utils import get_today
from app.utils.errors import CustomException
from app.web import templates, error_page

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def list_sellers(
        request: Request,
        search_text: str = "",
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "seller:read"], current_client)

    sellers = crud_sellers.get_sellers_list(db, search_text=search_text)

    return templates.TemplateResponse("sellers/sellers_list.html", {
        "request": request,
        "sellers": sellers,
        "total_results": len(sellers)
    })


@router.get("/create", response_class=HTMLResponse)
def create_seller(
        request: Request,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "seller:create"], current_client)

    return templates.TemplateResponse("sellers/sellers_create.html", {
        "request": request,
        "today": str(get_today())
    })


@router.post("/create", response_class=HTMLResponse)
async def create_seller_submit(
        request: Request,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "seller:create"], current_client)

    data = await request.form()

    try:
        seller_create: schemas.SellerCreate = schemas.SellerCreate(**data)

        seller = crud_sellers.create_seller(db=db, seller_create=seller_create)
    except (CustomException, ValidationError) as exc:
        return error_page(request, exc)

    return RedirectResponse(url=f"{seller.seller_id}/show", status_code=303)


@router.get("/{seller_id}/show", response_class=HTMLResponse)
def show_seller(
        request: Request,
        seller_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "seller:read"], current_client)

    try:
        seller = crud_sellers.get_seller(db, seller_id=seller_id)
    except CustomException as exc:
        return error_page(request, exc)

    return templates.TemplateResponse("sellers/sellers_show.html", {
        "request": request,
        "seller": seller,
        "today": get_today()
    })


@router.get("/{seller_id}/update", response_class=HTMLResponse)
def edit_seller(
        request: Request,
        seller_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "seller:update"], current_client)

    try:
        seller = crud_sellers.get_seller(db, seller_id=seller_id)
    except CustomException as exc:
        return error_page(request, exc)

    return templates.TemplateResponse("sellers/sellers_edit.html", {
        "request": request,
        "seller": seller
    })


@router.post("/{seller_id}/update", response_class=HTMLResponse)
async def update_seller(
        request: Request,
        seller_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "seller:update"], current_client)

    data = await request.form()

    try:
        seller_update: schemas.SellerUpdate = schemas.SellerUpdate(**data)

        db_seller = crud_sellers.get_seller_by_id(db, seller_id=seller_id)
        _ = crud_sellers.update_seller(db, db_seller=db_seller, seller_update=seller_update)
    except (CustomException, ValidationError) as exc:
        return error_page(request, exc)

    return RedirectResponse(url=f"show", status_code=303)

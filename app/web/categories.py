from fastapi import APIRouter, Request
from pydantic_core import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse

from app.db import crud_items, schemas, DB_SESSION
from app.sec import GET_CURRENT_WEB_CLIENT, TokenData, are_valid_scopes
from app.utils import get_today
from app.utils.errors import CustomException
from app.web import templates, error_page

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def list_categories(
        request: Request,
        search_text: str = "",
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "category:read"], current_client)

    try:
        categories = crud_items.get_categories_list(db, search_text=search_text)
    except CustomException as exc:
        return error_page(request, exc)

    return templates.TemplateResponse(request=request, name="categories/categories_list.html", context={
        "categories": categories,
        "total_results": len(categories)
    })


@router.get("/create", response_class=HTMLResponse)
def create_category(
        request: Request,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "category:create"], current_client)

    return templates.TemplateResponse(request=request, name="categories/categories_create.html", context={"today": str(get_today())})


@router.post("/create", response_class=HTMLResponse)
async def create_category_submit(
        request: Request,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "category:create"], current_client)

    data = await request.form()

    try:
        category_create: schemas.CategoryCreate = schemas.CategoryCreate(**data)

        category = crud_items.create_category(db=db, category_create=category_create)
    except (CustomException, ValidationError) as exc:
        return error_page(request, exc)

    return RedirectResponse(url=f"{category.category_id}/show", status_code=303)


@router.get("/{category_id}/show", response_class=HTMLResponse)
def show_category(
        request: Request,
        category_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "category:read"], current_client)

    try:
        category = crud_items.get_category(db, category_id=category_id)
    except CustomException as exc:
        return error_page(request, exc)

    return templates.TemplateResponse(request=request, name="categories/categories_show.html", context={
        "category": category,
        "today": get_today()
    })


@router.get("/{category_id}/update", response_class=HTMLResponse)
def edit_category(
        request: Request,
        category_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "category:update"], current_client)

    try:
        category = crud_items.get_category(db, category_id=category_id)
    except CustomException as exc:
        return error_page(request, exc)

    return templates.TemplateResponse(request=request, name="categories/categories_edit.html", context={"category": category})


@router.post("/{category_id}/update", response_class=HTMLResponse)
async def update_category(
        request: Request,
        category_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "category:update"], current_client)

    data = await request.form()

    try:
        category_update: schemas.CategoryUpdate = schemas.CategoryUpdate(**data)

        db_category = crud_items.get_category_by_id(db, category_id=category_id)
        _ = crud_items.update_category(db, db_category=db_category, category_update=category_update)
    except (CustomException, ValidationError) as exc:
        return error_page(request, exc)

    return RedirectResponse(url=f"show", status_code=303)

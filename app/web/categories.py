from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse

from app.db import crud_items, schemas, DB_SESSION
from app.sec import GET_CURRENT_WEB_CLIENT, TokenData, are_valid_scopes
from app.utils import get_today
from app.web import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def list_categories(
        request: Request,
        search_text: str = "",
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "category:read"], current_client)

    categories = crud_items.get_categories_list(db, search_text=search_text)

    return templates.TemplateResponse("categories/categories_list.html", {
        "request": request,
        "categories": categories,
        "total_results": len(categories)
    })


@router.get("/create", response_class=HTMLResponse)
def create_category(
        request: Request,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "category:create"], current_client)

    return templates.TemplateResponse("categories/categories_create.html", {
        "request": request,
        "today": str(get_today())
    })


@router.post("/create", response_class=HTMLResponse)
async def create_category_submit(
        request: Request,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "category:create"], current_client)

    data = await request.form()
    category_create: schemas.CategoryCreate = schemas.CategoryCreate(**data)

    category = crud_items.create_category(db=db, category_create=category_create)
    return RedirectResponse(url=f"{category.category_id}/show", status_code=303)


@router.get("/{category_id}/show", response_class=HTMLResponse)
def show_category(
        request: Request,
        category_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "category:read"], current_client)

    category = crud_items.get_category(db, category_id=category_id)
    return templates.TemplateResponse("categories/categories_show.html", {
        "request": request,
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

    category = crud_items.get_category(db, category_id=category_id)
    return templates.TemplateResponse("categories/categories_edit.html", {
        "request": request,
        "category": category
    })


@router.post("/{category_id}/update", response_class=HTMLResponse)
async def update_category(
        request: Request,
        category_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "category:update"], current_client)

    data = await request.form()
    category_update: schemas.CategoryUpdate = schemas.CategoryUpdate(**data)

    db_category = crud_items.get_category_by_id(db, category_id=category_id)
    _ = crud_items.update_category(db, db_category=db_category, category_update=category_update)
    return RedirectResponse(url=f"show", status_code=303)

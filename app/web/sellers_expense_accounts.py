from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse

from app.db import crud_sellers, schemas, DB_SESSION
from app.sec import GET_CURRENT_WEB_CLIENT, TokenData, are_valid_scopes
from app.utils import get_today
from app.web import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def list_expense_accounts(
        request: Request,
        search_text: str = "",
        do_filter: bool = False,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "expense_account:read"], current_client)

    if do_filter:
        expense_accounts = crud_sellers.get_expense_accounts_list(db, search_text=search_text)
    else:
        expense_accounts = []

    return templates.TemplateResponse("sellers/expense_accounts_list.html", {
        "request": request,
        "expense_accounts": expense_accounts,
        "total_results": len(expense_accounts)
    })


@router.get("/create", response_class=HTMLResponse)
def create_expense_account(
        request: Request,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "expense_account:create"], current_client)

    return templates.TemplateResponse("sellers/expense_accounts_create.html", {
        "request": request,
        "today": str(get_today())
    })


@router.post("/create", response_class=HTMLResponse)
async def create_expense_account_submit(
        request: Request,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:create", "expense_account:create"], current_client)

    data = await request.form()
    expense_account_create: schemas.sellers.ExpenseAccountCreate = schemas.sellers.ExpenseAccountCreate(**data)

    expense_account = crud_sellers.create_expense_account(db=db, expense_account_create=expense_account_create)
    return RedirectResponse(url=f"{expense_account.ea_id}/show", status_code=303)


@router.get("/{ea_id}/show", response_class=HTMLResponse)
def show_expense_account(
        request: Request,
        ea_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "expense_account:read"], current_client)

    expense_account = crud_sellers.get_expense_account(db, ea_id=ea_id)
    expense_account.expense_account_items = sorted(expense_account.expense_account_items, key=lambda mh: mh.tid, reverse=True)
    return templates.TemplateResponse("sellers/expense_accounts_show.html", {
        "request": request,
        "expense_account": expense_account,
        "today": get_today()
    })


@router.get("/{ea_id}/update", response_class=HTMLResponse)
def edit_expense_account(
        request: Request,
        ea_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "expense_account:update"], current_client)

    expense_account = crud_sellers.get_expense_account(db, ea_id=ea_id)
    return templates.TemplateResponse("sellers/expense_accounts_edit.html", {
        "request": request,
        "expense_account": expense_account
    })


@router.post("/{ea_id}/update", response_class=HTMLResponse)
async def update_expense_account(
        request: Request,
        ea_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:update", "expense_account:update"], current_client)

    data = await request.form()
    expense_account_update: schemas.sellers.ExpenseAccountUpdate = schemas.sellers.ExpenseAccountUpdate(**data)

    db_expense_account = crud_sellers.get_expense_account_by_id(db, ea_id=ea_id)
    _ = crud_sellers.update_expense_account(db, db_expense_account=db_expense_account, expense_account_update=expense_account_update)
    return RedirectResponse(url=f"show", status_code=303)

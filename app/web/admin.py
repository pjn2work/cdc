from fastapi import APIRouter, Request, status, Form
from starlette.responses import HTMLResponse, RedirectResponse

from app.sec import (
    are_valid_scopes,
    cred,
    GET_CURRENT_WEB_CLIENT,
    ip_filtering,
    hash_password,
    TokenData,
)
from app.web import templates

router = APIRouter()


# grep -r "are_valid_scopes(" * | grep -oP '\[\K[^\]]+' | tr ', ' '\n' | sort | uniq
possible_scopes = {
    "app:admin",
    "app:create",
    "app:read",
    "app:update",
    "category:create",
    "category:read",
    "category:update",
    "due_payment:create",
    "due_payment:read",
    "expense_account:create",
    "expense_account:read",
    "expense_account:update",
    "index:read",
    "item:create",
    "item:read",
    "item:update",
    "member:create",
    "member:read",
    "member:update",
    "member_donation:create",
    "member_donation:read",
    "member_due_payment:create",
    "member_due_payment:read",
    "member_due_payment:update",
    "member_item:create",
    "member_item:read",
    "member_item:update",
    "seller:create",
    "seller:read",
    "seller:update",
    "seller_item:create",
    "seller_item:read",
    "seller_item:update",
}


@router.get("/", response_class=HTMLResponse)
def admin_clients(
        request: Request,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:admin"], current_client)

    clients = cred.admin_get_all_clients()

    return templates.TemplateResponse(request=request, name="admin/admin_clients.html", context={
        "clients": clients,
        "possible_scopes": possible_scopes,
    })


@router.post("/remove", response_class=HTMLResponse)
def admin_remove_client(
        request: Request,
        client_id: str = Form(),
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:admin"], current_client)

    cred.admin_remove_client(client_id)

    return RedirectResponse(url="/web/admin/", status_code=status.HTTP_302_FOUND)


@router.post("/update", response_class=HTMLResponse)
def admin_update_client(
        request: Request,
        client_original_id: str = Form(),
        client_new_id: str = Form(),
        client_name: str = Form(),
        client_secret: str = Form(""),
        expire_after: str = Form(),
        client_scopes: str = Form(),
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:admin"], current_client)

    data = {
         "client_name": client_name,
         "client_secret": hash_password(client_secret) if client_secret else "",
         "scopes": client_scopes.split(","),
         "expire_after": float(expire_after)
      }
    cred.admin_update_client(client_original_id, client_new_id, data)

    return RedirectResponse(url="/web/admin/", status_code=status.HTTP_302_FOUND)


@router.get("/access_list", response_class=HTMLResponse)
def admin_access_list(
        request: Request,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:admin"], current_client)

    return templates.TemplateResponse(
        request=request,
        name="admin/admin_access_list.html",
        context={
            "thresholds": ip_filtering.get_thresholds(),
            "blocked_clients": ip_filtering.get_blocked_clients()
        }
    )


@router.post("/unblock", response_class=HTMLResponse)
def admin_unblock_client(
        request: Request,
        client: str = Form(),
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:admin"], current_client)

    ip_filtering.unblock_client(client)

    return RedirectResponse(url=f"access_list", status_code=303)


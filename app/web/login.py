from fastapi import HTTPException, status, APIRouter, Request
from starlette.responses import HTMLResponse, RedirectResponse

from app.sec import get_access_token, change_client_secret
from app.web import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@router.post("/submit", response_class=HTMLResponse)
async def login(request: Request):
    data = await request.form()
    client_id = data.get("client_id")
    client_secret = data.get("client_secret")

    try:
        token_response = get_access_token(client_id, client_secret)
        response = RedirectResponse(url="/web/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="access_token", value=token_response.access_token, httponly=True)
        return response
    except HTTPException as e:
        return templates.TemplateResponse(request=request, name="login.html", context={"error": e.detail}, status_code=401)


@router.post("/change_password", response_class=HTMLResponse)
async def login(request: Request):
    data = await request.form()
    client_id = data.get("client_id")
    client_secret = data.get("client_secret")
    new_client_secret = data.get("new_client_secret")

    try:
        change_client_secret(client_id, client_secret, new_client_secret)
        response = RedirectResponse(url="/web/", status_code=status.HTTP_302_FOUND)
        return response
    except HTTPException as e:
        return templates.TemplateResponse(request=request, name="login.html", context={"error": e.detail}, status_code=401)

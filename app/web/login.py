from fastapi import HTTPException, status, APIRouter, Request
from starlette.responses import HTMLResponse, RedirectResponse

from app.sec import get_access_token
from app.web import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def login(request: Request):
    data = await request.form()
    client_id = data.get("client_id")
    client_secret = data.get("client_secret")

    try:
        token_response = get_access_token(client_id, client_secret)
        response = RedirectResponse(url="/web/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="access_token", value=token_response["access_token"], httponly=True)
        return response
    except HTTPException as e:
        return templates.TemplateResponse("login.html", {"request": request, "error": e.detail})

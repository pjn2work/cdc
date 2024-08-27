from fastapi import APIRouter, Request
from starlette.responses import HTMLResponse

from app.sec import GET_CURRENT_WEB_CLIENT, TokenData, are_valid_scopes
from app.web import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index(
        request: Request,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    are_valid_scopes(["app:read", "index:read"], current_client)
    return templates.TemplateResponse(request=request, name="index.html", context={"username": current_client.name})

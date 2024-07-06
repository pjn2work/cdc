from fastapi import APIRouter, Request
from starlette.responses import HTMLResponse

from . import templates
from ..sec import GET_CURRENT_WEB_CLIENT, TokenData

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index(
        request: Request,
        current_client: TokenData = GET_CURRENT_WEB_CLIENT):
    return templates.TemplateResponse("index.html", {"request": request})

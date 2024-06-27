from fastapi import APIRouter, Request
from starlette.responses import HTMLResponse
from . import templates


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

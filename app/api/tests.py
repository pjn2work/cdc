from fastapi import APIRouter
from starlette.responses import HTMLResponse

from app.db.models import clear_db
from app.sec import TokenData, are_valid_scopes, GET_CURRENT_API_CLIENT

router = APIRouter()


@router.get("/reset", response_class=HTMLResponse)
def index(current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:test"], current_client)
    clear_db()
    return "DB is now cleared."

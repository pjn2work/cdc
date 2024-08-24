from fastapi import Request
from fastapi.templating import Jinja2Templates

from app import logit, logging, get_prev_function
from app.utils.errors import CustomException

templates = Jinja2Templates(directory="app/web/templates")


def error_page(request: Request, exc: Exception):
    status_code = exc.status_code if isinstance(exc, CustomException) else CustomException.status_code

    logit(msg=f"web.{status_code=} - {exc}", level=logging.INFO, func=get_prev_function())

    return templates.TemplateResponse("error.html", {
        "request": request,
        "error_message": str(exc),
        "status_code": status_code
    }, status_code=status_code)

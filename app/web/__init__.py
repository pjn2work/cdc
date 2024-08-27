from fastapi import Request
from fastapi.templating import Jinja2Templates

from app import logit, logging, get_prev_function, unified_response
from app.utils.errors import CustomException

templates = Jinja2Templates(directory="app/web/templates")


def error_page(request: Request, exc: Exception, level=logging.INFO):
    status_code = getattr(exc, "status_code", CustomException.status_code)

    logit(msg=f"web.{status_code=} - {exc}", level=level, func=get_prev_function())

    response = templates.TemplateResponse("error.html", {
        "request": request,
        "error_message": str(exc),
        "status_code": status_code
    }, status_code=status_code)

    return unified_response(response)

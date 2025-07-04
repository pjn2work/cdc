from fastapi import Request
from fastapi.templating import Jinja2Templates

from app import logit, logging, get_prev_function, unified_response
from app.utils.errors import CustomException

templates = Jinja2Templates(directory="app/web/templates")


def error_page(request: Request, exc: Exception, level=logging.INFO):
    status_code = getattr(exc, "status_code", CustomException.status_code)

    logit(msg=f"web.{status_code=} - {exc}", level=level, func=get_prev_function())

    response = templates.TemplateResponse(request=request, name="error.html", context={
        "error_message": str(exc),
        "status_code": status_code
    }, status_code=status_code)

    return unified_response(response)


def flash(request: Request, message: str, category: str = "success") -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append((category, message))

def get_flashed_messages(request: Request):
    return request.session.pop("_messages") if "_messages" in request.session else []

# Add get_flashed_messages to Jinja2 environment
templates.env.globals['get_flashed_messages'] = get_flashed_messages

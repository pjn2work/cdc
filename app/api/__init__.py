from fastapi.responses import JSONResponse

from app import logit, logging, get_prev_function, unified_response
from app.utils.errors import CustomException


def error_json(exc: Exception, level=logging.INFO):
    status_code = getattr(exc, "status_code", CustomException.status_code)

    logit(msg=f"api.{status_code=} - {exc}", level=level, func=get_prev_function())

    response = JSONResponse(status_code=status_code, content={"detail": str(exc)})

    return unified_response(response)

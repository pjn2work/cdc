from fastapi.responses import JSONResponse

from app import logit, logging, get_prev_function, unified_response
from app.utils.errors import CustomException


def error_json(exc: Exception):
    status_code = exc.status_code if isinstance(exc, CustomException) else CustomException.status_code

    logit(msg=f"api.{status_code=} - {exc}", level=logging.INFO, func=get_prev_function())

    response = JSONResponse(status_code=status_code, content={"detail": str(exc)})

    return unified_response(response)

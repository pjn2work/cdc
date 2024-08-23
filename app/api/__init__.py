from fastapi.responses import JSONResponse

from app.utils.errors import CustomException


def error_json(exc: Exception):
    status_code = exc.status_code if isinstance(exc, CustomException) else CustomException.status_code
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})

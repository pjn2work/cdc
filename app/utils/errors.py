class CustomException(Exception):
    status_code = 444

class NotFound404(CustomException):
    status_code = 404

class Conflict409(CustomException):
    status_code = 409

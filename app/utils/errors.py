class CustomException(Exception):
    status_code = 400

class NotFound404(CustomException):
    status_code = 404

class Conflict409(CustomException):
    status_code = 409

class TooManyRequests429(CustomException):
    status_code = 429

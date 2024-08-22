import inspect
import logging

log = logging.getLogger("CECC")


def logit(msg: str, level: int = logging.INFO):
    # Get the previous frame in the stack
    func = inspect.currentframe().f_back.f_code

    msg = f"{func.co_name}] - {msg}"
    log.log(level=level, msg=msg)

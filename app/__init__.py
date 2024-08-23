import inspect
import logging
from datetime import datetime


log = logging.getLogger("CECC")


class NoTracebackFilter(logging.Filter):
    def filter(self, record):
        if isinstance(record.exc_info, tuple):
            record.exc_info[1].__traceback__ = None
            record.exc_info[1].__suppress_context__ = True
        return True


for handler in logging.getLogger().handlers:
    handler.addFilter(NoTracebackFilter())


def logit(msg: str, level: int = logging.INFO, func = None):
    # Get the previous frame in the stack
    if func is None:
        func = inspect.currentframe().f_back.f_code

    msg = f"[{func.co_name}] - {msg}"
    log.log(level=level, msg=msg)


def log_traffic(status_code: int, start_time: datetime, method: str, url: str, client: str):
    process_time = (datetime.now() - start_time).total_seconds()
    log_params = {
        "method": method,
        "url": url,
        "status": status_code,
        "process_time": process_time,
        "client": client
    }
    logit(str(log_params), level=logging.DEBUG, func=inspect.currentframe().f_back.f_code)

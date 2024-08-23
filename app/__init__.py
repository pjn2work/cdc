import inspect
import logging

log = logging.getLogger("CECC")


class NoTracebackFilter(logging.Filter):
    def filter(self, record):
        if isinstance(record.exc_info, tuple):
            record.exc_info[1].__traceback__ = None
            record.exc_info[1].__suppress_context__ = True
        return True


for handler in logging.getLogger().handlers:
    handler.addFilter(NoTracebackFilter())


def logit(msg: str, level: int = logging.INFO):
    # Get the previous frame in the stack
    func = inspect.currentframe().f_back.f_code

    msg = f"[{func.co_name}] - {msg}"
    log.log(level=level, msg=msg)

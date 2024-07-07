import logging


log = logging.getLogger("CECC")
log.setLevel(logging.INFO)


def logit(msg: str, level: int = logging.INFO):
    log.log(level=level, msg=msg)

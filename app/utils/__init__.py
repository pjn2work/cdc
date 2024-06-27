from typing import Union
from datetime import datetime, date
from pytz import timezone


TZ = timezone("Europe/Lisbon")


def get_now() -> datetime:
    return datetime.now(TZ).replace(microsecond=0)


def get_today() -> date:
    return get_now().date()


def get_first_day(date_: date) -> date:
    return date(date_.year, date_.month, 1)


def get_today_year_month_str():
    return format_year_month(get_today())


def format_year_month(ym: Union[str, date]) -> str:
    if isinstance(ym, date):
        return ym.strftime("%Y-%m")

    if "-" not in ym:
        ym = ym[:4] + "-" + ym[4:6]
    year, month = list(map(int, ym.split('-')))
    return f"{year}-{month:02d}"

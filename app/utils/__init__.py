import json
import os.path
from base64 import urlsafe_b64encode, urlsafe_b64decode
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


def format_year_month(ym: str | date) -> str:
    if isinstance(ym, date):
        return ym.strftime("%Y-%m")

    if "-" not in ym:
        ym = ym[:4] + "-" + ym[4:6]
    year, month = list(map(int, ym.split('-')))
    return f"{year}-{month:02d}"


def read_json_file(file_name: str, same_as: str = "") -> dict:
    if same_as:
        file_name = os.path.join(os.path.dirname(same_as), file_name)

    with open(file_name, "r") as file:
        return json.load(file)

def b64encode_str(s: str) -> str:
    return urlsafe_b64encode(s.encode("utf-8")).decode("utf-8")

def b64decode_str(s: str) -> str:
    return urlsafe_b64decode(s.encode("utf-8")).decode("utf-8")

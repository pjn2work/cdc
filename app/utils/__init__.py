import json
from base64 import urlsafe_b64encode, urlsafe_b64decode
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from io import BytesIO

import pandas as pd
from fastapi.responses import StreamingResponse
from pytz import timezone

TZ = timezone("Europe/Lisbon")


def get_now() -> datetime:
    return datetime.now(TZ).replace(microsecond=0)


def get_now_as_str() -> str:
    return get_now().strftime("%Y-%m-%d %H:%M:%S")


def now_plus_timedelta_as_str(**kwargs) -> str:
    _dt = get_now() + timedelta(**kwargs)
    return _dt.strftime("%Y-%m-%d %H:%M:%S")


def get_today() -> date:
    return get_now().date()


def get_first_day(date_: date) -> date:
    return date(date_.year, date_.month, 1)


def get_today_year_month_str() -> str:
    return format_year_month(get_today())


def format_year_month(ym: str | date) -> str:
    if isinstance(ym, date):
        return ym.strftime("%Y-%m")

    if "-" not in ym:
        ym = ym[:4] + "-" + ym[4:6]
    year, month = list(map(int, ym.split('-')))
    return f"{year}-{month:02d}"


def str2date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def read_json_file(file_name: str) -> dict:
    with open(file_name, "r") as file:
        return json.load(file)


def save_json_file(file_name: str, data: dict):
    with open(file_name, "w") as file:
        json.dump(data, file, indent=3)


def b64encode_str(s: str) -> str:
    return urlsafe_b64encode(s.encode("utf-8")).decode("utf-8")

def b64decode_str(s: str) -> str:
    return urlsafe_b64decode(s.encode("utf-8")).decode("utf-8")


@dataclass
class DataframeSheet:
    df: pd.DataFrame
    sheet_name: str


def save_to_excel_sheets(*df_sheets: DataframeSheet, filename: str = "results.xlsx") -> StreamingResponse:
    # Save the DataFrame to an Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for dfs in df_sheets:
            if dfs.df is not None:
                dfs.df.to_excel(writer, index=False, sheet_name=dfs.sheet_name)
    output.seek(0)

    # Send the Excel file as a response
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

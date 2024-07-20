import datetime
import logging
from io import BytesIO
from typing import List, Tuple

import pandas as pd
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import func, and_, case as case_
from sqlalchemy.orm import Session

from app import logit
from app.db import models, schemas
from app.utils import get_now, get_today_year_month_str, format_year_month, str2date


def get_member_due_payment_missing_stats(db: Session, member_id: int) -> Tuple[List[str], int]:
    mdp_missing = db.query(models.MemberDuesPayment).filter_by(
        member_id=member_id, is_member_active=True, is_paid=False
    ).filter(
        models.MemberDuesPayment.id_year_month <= get_today_year_month_str()
    ).order_by(models.MemberDuesPayment.id_year_month).all()

    months_missing = [str(mdp.id_year_month) for mdp in mdp_missing]
    total_amount_missing = sum([mdp.amount for mdp in mdp_missing])

    return months_missing, total_amount_missing


def _calc_dues_payment_stats(db: Session, dp: models.DuesPayment) -> models.DuesPayment:
    dp.total_amount_paid, dp.total_members_paid = db.query(
        func.sum(models.MemberDuesPayment.amount), func.count(models.MemberDuesPayment.amount)
    ).filter_by(id_year_month=dp.id_year_month, is_paid=True, is_member_active=True).one()

    dp.total_amount_missing, dp.total_members_missing = db.query(
        func.sum(models.MemberDuesPayment.amount), func.count(models.MemberDuesPayment.amount)
    ).filter_by(id_year_month=dp.id_year_month, is_paid=False, is_member_active=True).one()
    return dp


def get_due_payment_year_month_stats(db: Session, id_year_month: str) -> models.DuesPayment:
    _dp = db.get(models.DuesPayment, id_year_month)
    if _dp is None:
        raise HTTPException(status_code=404, detail=f"Due Payment {id_year_month} not found")
    return _calc_dues_payment_stats(db, _dp)


def get_dues_payment_year_month_stats_list(
        db: Session,
        since: str = None,
        until: str = None
) -> List[schemas.dues_payments.DuesPaymentView]:
    _dp_list = db.query(models.DuesPayment)
    if since:
        since = format_year_month(since)
        _dp_list = _dp_list.filter(models.DuesPayment.id_year_month >= since)
    if until:
        until = format_year_month(until)
        _dp_list = _dp_list.filter(models.DuesPayment.id_year_month <= until)
    _dp_list = _dp_list.order_by(models.DuesPayment.date_ym).all()

    results = []
    for _dp in _dp_list:
        dps = _calc_dues_payment_stats(db, _dp)
        results.append(dps)
    return results


def create_dues_payment_year_month(db: Session, dues_payment_create: schemas.dues_payments.DuesPaymentCreate) -> models.DuesPayment:
    dp = schemas.dues_payments.DuesPayment(**dues_payment_create.model_dump())
    db_dues_payment = models.DuesPayment(**dp.model_dump())

    try:
        db.add(db_dues_payment)
        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Due Payment {dp.date_ym} was already created, no need to create a new one.")

    _make_due_payment_for_active_members(db=db, id_year_month=db_dues_payment.id_year_month, date_ym=db_dues_payment.date_ym)
    _make_due_payment_for_non_active_members(db=db, id_year_month=db_dues_payment.id_year_month, date_ym=db_dues_payment.date_ym)

    db.refresh(db_dues_payment)
    _calc_dues_payment_stats(db, db_dues_payment)

    return db_dues_payment


def _make_due_payment_for_non_active_members(db: Session, id_year_month: str, date_ym: datetime.date) -> None:
    _member_list = db.query(models.Member).filter_by(is_active=False).filter(
        models.Member.start_date <= date_ym
    ).all()
    now = get_now()
    try:
        for member in _member_list:
            logit(f"Creating 0.0€ Due Payment for member={member.member_id} for {id_year_month} month.", logging.INFO)
            mdp = models.MemberDuesPayment(
                member_id=member.member_id,
                id_year_month=id_year_month,
                amount=0.0,
                is_paid=True,
                is_member_active=False,
                pay_update_time=now
            )
            db.add(mdp)
        db.commit()
    except:
        db.rollback()
        raise


def _make_due_payment_for_active_members(db: Session, id_year_month: str, date_ym: datetime.date) -> None:
    _member_list = db.query(models.Member).filter_by(is_active=True).filter(
        models.Member.start_date <= date_ym
    ).all()
    try:
        for member in _member_list:
            _make_due_payment_for_member(db=db, id_year_month=id_year_month, member=member)
        db.commit()
    except:
        db.rollback()
        raise


def make_due_payment_for_new_member(db: Session, member: models.Member) -> None:
    _dp_list = db.query(models.DuesPayment).filter(models.DuesPayment.date_ym >= member.start_date).all()
    try:
        for _dp in _dp_list:
            _make_due_payment_for_member(db=db, id_year_month=_dp.id_year_month, member=member)
        db.commit()
    except:
        db.rollback()
        raise


def _make_due_payment_for_member(db: Session, id_year_month: str, member: models.Member) -> None:
    logit(f"Creating missing {member.amount}€ Due Payment for member={member.member_id} for {id_year_month} month.", logging.INFO)
    mdp = models.MemberDuesPayment(
        member_id=member.member_id,
        id_year_month=id_year_month,
        amount=member.amount,
        is_paid=False,
        is_member_active=True,
        pay_update_time=get_now()
    )
    db.add(mdp)

    # update member stats
    member.total_months_missing += 1
    member.total_amount_missing += member.amount
    db.add(member)


def get_member_due_payment(db: Session, tid: int) -> models.MemberDuesPayment:
    mdp: models.MemberDuesPayment = db.get(models.MemberDuesPayment, tid)
    if mdp is None:
        raise HTTPException(status_code=404, detail=f"MemberDuesPayment {tid} not found")
    return mdp


def pay_member_due_payment(
        db: Session,
        tid:int,
        mdpc: schemas.member_due_payment.MemberDuesPaymentCreate
) -> models.MemberDuesPayment:
    mdp: models.MemberDuesPayment = db.get(models.MemberDuesPayment, tid)
    if mdp is None:
        raise ValueError(f"MemberDuesPayment={tid} not found.")

    if mdp.is_paid:
        raise ValueError(f"MemberDuesPayment={tid} {mdp.id_year_month} was already paid for member={mdp.member_id} and the amount {mdp.amount}€.")

    if not mdp.is_member_active:
        raise ValueError(f"Member={mdp.member_id} is not active for payment at {mdp.id_year_month} MemberDuesPayment={tid}.")

    try:
        mdp.is_paid = True
        mdp.is_cash = mdpc.is_cash
        mdp.pay_date = mdpc.pay_date
        mdp.pay_update_time = get_now()
        db.add(mdp)

        # update member stats
        member = db.get(models.Member, mdp.member_id)
        member.total_months_paid += 1
        member.total_amount_paid += mdp.amount
        member.total_months_missing -= 1
        member.total_amount_missing -= mdp.amount
        db.add(member)

        db.commit()
    except:
        db.rollback()
        raise

    db.refresh(mdp)
    return mdp


def get_df_pivot_table_dues_paid_for_all_members(
        db: Session,
        months: List[str],
        month_cases: List,
        is_paid: bool) -> pd.DataFrame:
    # Construct the query
    query = db.query(
        models.Member.member_id,
        models.Member.name,
        *month_cases
    ).filter(and_(
        models.MemberDuesPayment.is_member_active==True,
        models.MemberDuesPayment.is_paid==is_paid)
    ).join(
        models.MemberDuesPayment
    ).group_by(
        models.Member.member_id
    )

    results = query.all()
    if results:
        # Convert results to a DataFrame
        multiplier = 1 if is_paid else -1
        data = [
            {id_year_month: getattr(row, id_year_month) * multiplier for id_year_month in months}
            for row in results
        ]
        for i, row in enumerate(results):
            data[i]["ID"] = row.member_id
            data[i]["Nome"] = row.name
            data[i]["Total"] = sum(row[2:]) * multiplier

        # Create DataFrame with wanted columns
        df = pd.DataFrame(data)
        df = df[["ID", "Nome", "Total"] + months]
        df = df.sort_values(by=["ID"], inplace=False)
    else:
        df = pd.DataFrame(columns=["ID", "Nome", "Total"])

    return df


def pivot_table_dues_paid_for_all_members(
        db: Session,
        since: str = None,
        until: str = None,
        just_download: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame] | StreamingResponse:
    # Define the months you are interested in
    months_query = db.query(models.DuesPayment.id_year_month).order_by(models.DuesPayment.id_year_month)
    if since:
        since = format_year_month(since)
        months_query = months_query.filter(models.DuesPayment.date_ym >= since)
    if until:
        until = format_year_month(until)
        months_query = months_query.filter(models.DuesPayment.date_ym <= until)
    months = [str(id_year_month[0]) for id_year_month in months_query.all()]

    # Build the case statements for each month
    month_cases = [
        func.sum(
            case_(
            (models.MemberDuesPayment.id_year_month == id_year_month, models.MemberDuesPayment.amount), else_=0
            )
        ).label(id_year_month)
        for id_year_month in months
    ]

    df_paid = get_df_pivot_table_dues_paid_for_all_members(db, months=months, month_cases=month_cases, is_paid=True)
    df_missing = get_df_pivot_table_dues_paid_for_all_members(db, months=months, month_cases=month_cases, is_paid=False)

    if just_download:
        filename = f"CECC Associados Quotas de {since or months[0]} a {until or months[-1]}.xlsx"

        # Save the DataFrame to an Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            if df_paid is not None:
                df_paid.to_excel(writer, index=False, sheet_name="Quotas pagas")
            if df_missing is not None:
                df_missing.to_excel(writer, index=False, sheet_name="Quotas em atraso")
        output.seek(0)

        # Send the Excel file as a response
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    return df_paid, df_missing


def list_member_dues_payments_order_by_pay_date(
        db: Session,
        since: str = None,
        until: str = None,
        just_download: bool = False,
) -> List[models.MemberDuesPayment] | StreamingResponse:
    # Query between months for paid dues
    months_query = db.query(
        models.MemberDuesPayment
    ).filter_by(
        is_paid=True,
        is_member_active=True
    ).order_by(
        models.MemberDuesPayment.pay_date.desc(),
        models.MemberDuesPayment.member_id,
        models.MemberDuesPayment.pay_update_time.desc(),
    )
    if since:
        since = str2date(since)
        months_query = months_query.filter(models.MemberDuesPayment.pay_date >= since)
    if until:
        until = str2date(until)
        months_query = months_query.filter(models.MemberDuesPayment.pay_date <= until)

    mdp_list: List[models.MemberDuesPayment] = months_query.all()
    if not mdp_list:
        return []

    # Create pandas Dataframe
    if just_download:
        _data = [
            {
                "ID": mdp.member_id,
                "Nome": mdp.member.name,
                "Quota": mdp.id_year_month,
                "Valor": mdp.amount,
                "V.D.": mdp.is_cash,
                "Data Pagamento": mdp.pay_date,
                "Data Actualização": mdp.pay_update_time,
            }
            for mdp in mdp_list
        ]
        _df = pd.DataFrame(_data)
        since = since or _df['Quota'].min()
        until = until or _df['Quota'].max()

        # Create file
        filename = f"CECC Lista de pagamento de Quotas de {since} a {until}.xlsx"

        # Save the DataFrame to an Excel file
        _output = BytesIO()
        with pd.ExcelWriter(_output, engine="openpyxl") as writer:
            _df.to_excel(writer, index=False, sheet_name="Quotas pagas")
        _output.seek(0)

        return StreamingResponse(
            _output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    return mdp_list

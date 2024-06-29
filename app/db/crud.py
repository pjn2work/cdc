import datetime
import pandas as pd

from io import BytesIO
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import func, or_, and_, case as case_
from sqlalchemy.orm import Session
from typing import List, Tuple
from . import models, schemas
from ..utils import get_now, get_today_year_month_str, format_year_month
from .. import logit


def _get_member_due_payment_missing_stats(db: Session, member_id: int) -> Tuple[List[str], int]:
    mdp_missing = db.query(models.MemberDuesPayment).filter_by(
        member_id=member_id, is_member_active=True, is_paid=False
    ).filter(
        models.MemberDuesPayment.id_year_month <= get_today_year_month_str()
    ).order_by(models.MemberDuesPayment.id_year_month).all()

    months_missing = [mdp.id_year_month for mdp in mdp_missing]
    total_amount_missing = sum([mdp.amount for mdp in mdp_missing])

    return months_missing, total_amount_missing


def get_member_by_id(db: Session, member_id: int) -> models.Member:
    member = db.get(models.Member, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail=f"Member {member_id} not found")
    return member


def get_member(db: Session, member_id: int) -> models.Member:
    member = get_member_by_id(db, member_id)

    months_missing, total_amount_missing = _get_member_due_payment_missing_stats(db, member_id)

    member.months_missing = months_missing
    member.total_months_missing = len(months_missing)
    member.total_amount_missing = total_amount_missing

    return member


def _get_all_members(db: Session,
                     active_members: bool = None,
                     search_text: str = None,
                     skip: int = 0, limit: int = 1000) -> List[models.Member]:
    _dbq = db.query(models.Member)

    if active_members is not None:
        _dbq = _dbq.filter_by(is_active=active_members)

    if search_text is not None:
        _dbq = _dbq.filter(or_(
            models.Member.name.ilike(f"%{search_text}%"),
            models.Member.tlf.ilike(f"%{search_text}%"),
            models.Member.email.ilike(f"%{search_text}%"),
        ))

    return _dbq.offset(skip).limit(limit).all()


def get_members_list(db: Session,
                     skip: int = 0, limit: int = 1000,
                     only_due_missing: bool = None,
                     only_active_members: bool = None,
                     search_text: str = "") -> List[models.Member]:
    _all_members_filtered = _get_all_members(db, only_active_members, search_text, skip=skip, limit=limit)

    if only_due_missing is None:
        return _all_members_filtered

    is_dues_payments_empty = db.query(models.DuesPayment).first() is None
    if is_dues_payments_empty and only_due_missing:
        return []

    _this_month = get_today_year_month_str()
    result = []
    for member in _all_members_filtered:
        mdps = []
        for mdp in member.member_due_payment:
            if only_due_missing:
                if not mdp.is_paid and mdp.is_member_active and mdp.id_year_month <= _this_month:
                    mdps.append(mdp.amount)
            else:
                if mdp.is_paid and mdp.is_member_active:
                    mdps.append(mdp.amount)
        if mdps:
            if only_due_missing:
                member.total_months_missing = len(mdps)
                member.total_amount_missing = sum(mdps)
            result.append(member)
    return result


def create_member(db: Session, member: schemas.members.MemberCreate) -> models.Member:
    db_member = models.Member(**member.model_dump())
    try:
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
    except:
        db.rollback()
        raise

    _member_id = db_member.member_id
    _make_due_payment_for_new_member(db=db, member=db_member)
    _create_member_history(db=db, member=get_member_by_id(db, _member_id))

    return db_member


def update_member(db: Session, db_member: models.Member, member_update: schemas.members.MemberUpdate) -> models.Member:
    update_data = member_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_member, key, value)

    try:
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
    except:
        db.rollback()
        raise

    _create_member_history(db=db, member=db_member)

    return db_member


def update_member_active(db: Session, db_member: models.Member, member_update: schemas.members.MemberUpdateActive) -> models.Member:
    since = member_update.since
    now = get_now()

    if db_member.is_active == member_update.is_active:
        raise HTTPException(status_code=400, detail=f"Member {db_member.member_id} was already active set to {member_update.is_active}.")

    try:
        db_member.is_active = member_update.is_active

        # activating member - create new due payments missing
        if member_update.is_active:
            mdpl = db.query(
                models.MemberDuesPayment
            ).filter_by(
                member_id=db_member.member_id, is_paid=True, is_member_active=False
            ).filter(models.MemberDuesPayment.id_year_month >= since).all()
            for mdp in mdpl:
                # update member stats
                db_member.total_months_missing += 1
                db_member.total_amount_missing += db_member.amount

                # set MemberDuesPayment for re-activated user
                mdp.is_paid = False
                mdp.is_member_active = True
                mdp.amount = db_member.amount
                mdp.pay_date_time = now

                db.add(mdp)
        else:
            # deactivate member - delete future due payments
            mdpl = db.query(
                models.MemberDuesPayment
            ).filter_by(
                member_id=db_member.member_id, is_paid=False, is_member_active=True
            ).all()
            for mdp in mdpl:
                if mdp.id_year_month >= since:
                    # update member stats
                    db_member.total_months_missing -= 1
                    db_member.total_amount_missing -= mdp.amount

                    # set MemberDuesPayment 0 eur for inactive user
                    mdp.is_paid = True
                    mdp.is_member_active = False
                    mdp.amount = 0.0
                    mdp.pay_date_time = now

                    db.add(mdp)

        db.commit()
    except:
        db.rollback()
        raise

    db_member = update_member(db, db_member, member_update)
    return db_member


def update_member_amount(db: Session, db_member: models.Member, member_update: schemas.members.MemberUpdateAmount) -> models.Member:
    if not db_member.is_active:
        raise HTTPException(status_code=400, detail=f"Member={db_member.member_id} is not active.")

    mdpl = db.query(models.MemberDuesPayment).filter_by(
        member_id=db_member.member_id,
        is_paid=False
    ).filter(
        models.MemberDuesPayment.id_year_month >= member_update.since
    ).all()
    try:
        for mdp in mdpl:
            # change future due payments
            db_member.total_amount_missing += member_update.amount - mdp.amount
            mdp.amount = member_update.amount
            db.add(mdp)

        db.add(db_member)
        db.commit()
    except:
        db.rollback()
        raise

    db_member = update_member(db, db_member, member_update)
    return db_member


def _create_member_history(db: Session, member: models.Member) -> schemas.members.MemberHistory:
    args = {
        "since": get_today_year_month_str(),
        "date_time": get_now()
    }
    args.update(**_get_fields(member.__dict__))
    db_member_history = models.MemberHistory(**args)

    try:
        db.add(db_member_history)
        db.commit()
        db.refresh(db_member_history)
    except:
        db.rollback()
        raise

    return db_member_history


# vvvvv MemberDuesPayment vvvvv #


def _calc_dues_payment_stats(db: Session, dp: models.DuesPayment) -> schemas.dues_payments.DuesPaymentStats:
    dp.total_amount_paid, dp.total_members_paid = db.query(
        func.sum(models.MemberDuesPayment.amount), func.count(models.MemberDuesPayment.amount)
    ).filter_by(id_year_month=dp.id_year_month, is_paid=True, is_member_active=True).one()

    dp.total_amount_missing, dp.total_members_missing = db.query(
        func.sum(models.MemberDuesPayment.amount), func.count(models.MemberDuesPayment.amount)
    ).filter_by(id_year_month=dp.id_year_month, is_paid=False, is_member_active=True).one()
    return dp


def get_due_payment_year_month_stats(db: Session, id_year_month: str) -> schemas.dues_payments.DuesPaymentStats:
    _dp = db.get(models.DuesPayment, id_year_month)
    if _dp is None:
        raise HTTPException(status_code=404, detail=f"Due Payment {id_year_month} not found")
    return _calc_dues_payment_stats(db, _dp)


def get_dues_payment_year_month_stats_list(db: Session, since: str = None, until: str = None) -> List[schemas.dues_payments.DuesPaymentStats]:
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
        _calc_dues_payment_stats(db, _dp)
        results.append(_dp)
    return results


def create_dues_payment_year_month(db: Session, dues_payment: schemas.dues_payments.DuesPaymentCreate) -> models.DuesPayment:
    dp = schemas.dues_payments.DuesPayment(**dues_payment.model_dump())
    db_dues_payment = models.DuesPayment(**dp.model_dump())

    try:
        db.add(db_dues_payment)
        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Due month {dp.date_ym} was already created, no need to create a new one.")

    _make_due_payment_for_active_members(db=db, id_year_month=db_dues_payment.id_year_month, date_ym=db_dues_payment.date_ym)
    _make_due_payment_for_non_active_members(db=db, id_year_month=db_dues_payment.id_year_month, date_ym=db_dues_payment.date_ym)

    db.refresh(db_dues_payment)
    return db_dues_payment


def _make_due_payment_for_non_active_members(db: Session, id_year_month: str, date_ym: datetime.date):
    _member_list = db.query(models.Member).filter_by(is_active=False).filter(
        models.Member.start_date <= date_ym
    ).all()
    now = get_now()
    try:
        for member in _member_list:
            logit(f"Creating 0.0€ Due Payment for member={member.member_id} for {id_year_month} month.")
            mdp = models.MemberDuesPayment(
                member_id=member.member_id,
                id_year_month=id_year_month,
                amount=0.0,
                is_paid=True,
                is_member_active=False,
                pay_date_time=now
            )
            db.add(mdp)
        db.commit()
    except:
        db.rollback()
        raise


def _make_due_payment_for_active_members(db: Session, id_year_month: str, date_ym: datetime.date):
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


def _make_due_payment_for_new_member(db: Session, member: models.Member):
    _dp_list = db.query(models.DuesPayment).filter(models.DuesPayment.date_ym >= member.start_date).all()
    try:
        for _dp in _dp_list:
            _make_due_payment_for_member(db=db, id_year_month=_dp.id_year_month, member=member)
        db.commit()
    except:
        db.rollback()
        raise


def _make_due_payment_for_member(db: Session, id_year_month: str, member: models.Member):
    logit(f"Creating missing {member.amount}€ Due Payment for member={member.member_id} for {id_year_month} month.")
    mdp = models.MemberDuesPayment(
        member_id=member.member_id,
        id_year_month=id_year_month,
        amount=member.amount,
        is_paid=False,
        is_member_active=True,
        pay_date_time=get_now()
    )
    db.add(mdp)

    # update member stats
    member.total_months_missing += 1
    member.total_amount_missing += member.amount
    db.add(member)


def get_member_due_payment(db: Session, tid: int) -> models.MemberDuesPayment:
    mdp = db.get(models.MemberDuesPayment, tid)
    if mdp is None:
        raise HTTPException(status_code=404, detail=f"MemberDuesPayment={tid} not found.")
    return mdp


def pay_member_due_payment(db: Session, tid:int):
    mdp = db.get(models.MemberDuesPayment, tid)
    if mdp is None:
        raise ValueError(f"MemberDuesPayment={tid} not found.")

    if mdp.is_paid:
        raise ValueError(f"MemberDuesPayment={tid} {mdp.id_year_month} was already paid for member={mdp.member_id} and the amount {mdp.amount}€.")

    if not mdp.is_member_active:
        raise ValueError(f"Member={mdp.member_id} is not active for payment at {mdp.id_year_month} MemberDuesPayment={tid}.")

    try:
        mdp.is_paid = True
        mdp.pay_date_time = get_now()  # mdpu.pay_date_time
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


def get_df_pivot_table_dues_paied_for_all_members(
        db: Session,
        months: List[str],
        month_cases: List,
        is_paied: bool) -> pd.DataFrame:
    # Construct the query
    query = db.query(
        models.Member.member_id,
        models.Member.name,
        *month_cases
    ).filter(and_(
        models.MemberDuesPayment.is_member_active==True,
        models.MemberDuesPayment.is_paid==is_paied)
    ).join(
        models.MemberDuesPayment
    ).group_by(
        models.Member.member_id
    )

    # Execute the query and fetch the results
    results = query.all()

    # Convert results to a DataFrame
    multiplier = 1 if is_paied else -1
    data = [
        {id_year_month: getattr(row, id_year_month) * multiplier for id_year_month in months}
        for row in results
    ]
    for i, row in enumerate(results):
        data[i]["member_id"] = row.member_id
        data[i]["name"] = row.name
        data[i]["total"] = sum(row[2:]) * multiplier

    # Create DataFrame with wanted columns
    df = pd.DataFrame(data)
    df = df[["member_id", "name", "total"] + months]
    df = df.sort_values(by=["member_id"], inplace=False)

    return df


def pivot_table_dues_paied_for_all_members(db: Session, since: str = None, until: str = None):
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

    df_paied = get_df_pivot_table_dues_paied_for_all_members(db, months=months, month_cases=month_cases, is_paied=True)
    df_missing = get_df_pivot_table_dues_paied_for_all_members(db, months=months, month_cases=month_cases, is_paied=False)

    filename = f"CdC Membros Quotas de {since or months[0]} a {until or months[-1]}.xlsx"

    # Save the DataFrame to an Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_paied.to_excel(writer, index=False, sheet_name="Quotas pagas")
        df_missing.to_excel(writer, index=False, sheet_name="Quotas em atraso")
    output.seek(0)

    # Send the Excel file as a response
    return df_paied, df_missing, StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def _get_fields(d: dict) -> dict:
    return {k: v for k, v in d.items() if not k.startswith("_")}

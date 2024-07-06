from io import BytesIO
from typing import List

import pandas as pd
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from . import models, schemas
from .crud_dues_payments import get_member_due_payment_missing_stats, make_due_payment_for_new_member
from ..utils import get_now, get_today_year_month_str


def get_member_by_id(db: Session, member_id: int) -> models.Member:
    member = db.get(models.Member, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail=f"Member {member_id} not found")
    return member


def get_member(db: Session, member_id: int) -> models.Member:
    member = get_member_by_id(db, member_id)

    months_missing, total_amount_missing = get_member_due_payment_missing_stats(db, member_id)

    member.months_missing = months_missing
    member.total_months_missing = len(months_missing)
    member.total_amount_missing = total_amount_missing

    return member


def _get_all_members(
        db: Session,
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
            models.Member.notes.ilike(f"%{search_text}%"),
        ))

    return _dbq.offset(skip).limit(limit).all()


def get_members_list(
        db: Session,
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


def create_member(db: Session, member_create: schemas.members.MemberCreate) -> models.Member:
    db_member = models.Member(**member_create.model_dump())
    try:
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
    except:
        db.rollback()
        raise

    _member_id = db_member.member_id
    make_due_payment_for_new_member(db=db, member=db_member)
    _create_member_history(db=db, member=get_member_by_id(db, _member_id))

    return db_member


def update_member(
        db: Session,
        db_member: models.Member,
        member_update: schemas.members.MemberUpdate) -> models.Member:
    update_data = member_update.model_dump(exclude_unset=True)
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


def update_member_active(
        db: Session,
        db_member: models.Member,
        member_update: schemas.members.MemberUpdateActive) -> models.Member:
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
                mdp.pay_update_time = now

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
                    mdp.pay_update_time = now

                    db.add(mdp)

        db.commit()
    except:
        db.rollback()
        raise

    db_member = update_member(db, db_member, member_update)
    return db_member


def update_member_amount(
        db: Session,
        db_member: models.Member,
        member_update: schemas.members.MemberUpdateAmount) -> models.Member:
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


def post_member_donation(db: Session, member_id: int, member_donation_create: schemas.member_donations.MemberDonationCreate):
    db_member_donation = models.MemberDonation(member_id=member_id, **member_donation_create.model_dump())
    db_member_donation.pay_update_time = get_now()
    try:
        db.add(db_member_donation)
        db.commit()
        db.refresh(db_member_donation)
    except:
        db.rollback()
        raise

    db_member = get_member_by_id(db, member_id)
    return db_member


def list_member_donations_order_by_pay_date(
        db: Session,
        since: str = None,
        until: str = None,
        just_download: bool = False,
) -> List[models.MemberDonation] | StreamingResponse:
    # Query between months for paid dues
    months_query = db.query(
        models.MemberDonation
    ).order_by(
        models.MemberDonation.pay_date.desc(),
        models.MemberDonation.member_id,
        models.MemberDonation.pay_update_time.desc(),
    )
    if since:
        months_query = months_query.filter(models.MemberDonation.pay_date >= since)
    if until:
        months_query = months_query.filter(models.MemberDonation.pay_date <= until)

    md_list: List[models.MemberDonation] = months_query.all()
    if not md_list:
        return []

    # Create pandas Dataframe
    if just_download:
        _data = [
            {
                "Associado ID": md.member_id,
                "Nome": md.member.name,
                "Valor": md.amount,
                "Data Pagamento": md.pay_date,
                "Data Actualização": md.pay_update_time,
            }
            for md in md_list
        ]
        _df = pd.DataFrame(_data)
        since = since or _df['Data Pagamento'].min()
        until = until or _df['Data Pagamento'].max()

        # Create file
        filename = f"CECC Lista de donativos de {since} a {until}.xlsx"

        # Save the DataFrame to an Excel file
        _output = BytesIO()
        with pd.ExcelWriter(_output, engine="openpyxl") as writer:
            _df.to_excel(writer, index=False, sheet_name="Donativos")
        _output.seek(0)

        return StreamingResponse(
            _output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    return md_list


def _get_fields(d: dict) -> dict:
    return {k: v for k, v in d.items() if not k.startswith("_")}

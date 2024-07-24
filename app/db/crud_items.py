from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import or_, desc
from sqlalchemy.orm import Session

from app.db import models, schemas
from app.db.crud_member import update_member_stats
from app.db.crud_sellers import update_expense_account_stats, update_seller_stats
from app.utils import get_now


def create_item(
        db: Session,
        item_create: schemas.ItemCreate
) -> models.Item:
    db_item = models.Item(**item_create.model_dump())
    db_item.row_update_time = get_now()
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
    except:
        db.rollback()
        raise

    return db_item


def get_items_list(db: Session, search_text: str, skip: int = 0, limit: int = 1000, category_id: Optional[int] = None) -> List[models.Item]:
    _dbq = db.query(models.Item)

    if search_text is not None:
        _dbq = _dbq.filter(or_(
            models.Item.name.ilike(f"%{search_text}%"),
            models.Item.notes.ilike(f"%{search_text}%"),
        ))
    if category_id:
        _dbq = _dbq.filter_by(category_id=category_id)

    return _dbq.offset(skip).limit(limit).all()

def _update_item_and_category_stats(db: Session, item_id: int) -> models.Item:
    db_item = get_item_by_id(db, item_id)

    _result_sellers = db.query(
        models.SellerItems
    ).filter_by(
        item_id=item_id
    ).all()

    _result_members = db.query(
        models.MemberItems
    ).filter_by(
        item_id=item_id
    ).all()

    db_item.total_quantity_seller_sold = sum([row.quantity for row in _result_sellers])
    db_item.total_amount_seller_sold = sum([row.total_price for row in _result_sellers])
    db_item.total_quantity_member_sold = sum([row.quantity for row in _result_members])
    db_item.total_amount_member_sold = sum([row.total_price for row in _result_members])

    try:
        db.add(db_item)
        db.commit()

        _update_category_stats(db, db_item.category_id)
    except:
        db.rollback()
        raise

    db.refresh(db_item)
    return db_item


def get_item_by_id(db: Session, item_id: int) -> models.Item:
    db_item = db.get(models.Item, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return db_item


def get_item(db: Session, item_id: int) -> models.Item:
    return get_item_by_id(db, item_id)


def update_item(
        db: Session,
        db_item: models.Item,
        item_update: schemas.ItemUpdate
) -> models.Item:
    old_category = db_item.category_id
    db_item.row_update_time = get_now()
    update_data = item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)

    try:
        db.add(db_item)
        db.commit()

        if "category_id" in update_data:
            _update_category_stats(db, old_category)
        _update_item_and_category_stats(db, db_item.item_id)
    except:
        db.rollback()
        raise

    db.refresh(db_item)
    return db_item


# ----------------------------------------------------------


def create_category(
        db: Session,
        category_create: schemas.CategoryCreate
) -> models.Category:
    db_category = models.Category(**category_create.model_dump())
    db_category.row_update_time = get_now()
    try:
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
    except:
        db.rollback()
        raise

    return db_category


def get_categories_list(db: Session, search_text: str, skip: int = 0, limit: int = 1000) -> List[models.Category]:
    _dbq = db.query(models.Category)

    if search_text is not None:
        _dbq = _dbq.filter(or_(
            models.Category.name.ilike(f"%{search_text}%"),
            models.Category.notes.ilike(f"%{search_text}%"),
        ))

    return _dbq.offset(skip).limit(limit).all()


def _update_category_stats(db: Session, category_id: int) -> models.Category:
    db_category = get_category_by_id(db, category_id)

    _result_sellers = db.query(
        models.SellerItems
    ).join(
        models.Item
    ).filter(
        models.Item.category_id == category_id
    ).all()

    _result_members = db.query(
        models.MemberItems
    ).join(
        models.Item
    ).filter(
        models.Item.category_id == category_id
    ).all()

    db_category.total_quantity_seller_sold = sum([row.quantity for row in _result_sellers])
    db_category.total_amount_seller_sold = sum([row.total_price for row in _result_sellers])
    db_category.total_quantity_member_sold = sum([row.quantity for row in _result_members])
    db_category.total_amount_member_sold = sum([row.total_price for row in _result_members])

    try:
        db.add(db_category)
        db.commit()
    except:
        db.rollback()
        raise

    db.refresh(db_category)
    return db_category


def get_category_by_id(db: Session, category_id: int) -> models.Category:
    db_category = db.get(models.Category, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail=f"Category {category_id} not found")
    return db_category


def get_category(db: Session, category_id: int) -> models.Category:
    return get_category_by_id(db, category_id)


def update_category(db: Session, db_category: models.Category, category_update: schemas.CategoryUpdate) -> models.Category:
    db_category.row_update_time = get_now()
    update_data = category_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)

    try:
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
    except:
        db.rollback()
        raise

    return db_category


# ----------------------------------------------------------


def create_seller_item(db: Session, item_id: int, seller_item_create: schemas.SellerItemsCreate) -> models.SellerItems:
    db_seller_item = models.SellerItems(item_id=item_id, **seller_item_create.model_dump())
    db_seller_item.row_update_time = get_now()

    try:
        db.add(db_seller_item)
        db.commit()

        update_expense_account_stats(db, db_seller_item.ea_id)
        update_seller_stats(db, db_seller_item.seller_id)
        _update_item_and_category_stats(db, db_seller_item.item_id)
    except:
        db.rollback()
        raise

    db.refresh(db_seller_item)
    return db_seller_item


def get_item_sellers_list(db: Session, item_id: int, skip: int, limit: int, search_text: str) -> List[models.SellerItems]:
    _dbq = db.query(models.SellerItems).filter_by(item_id=item_id)

    if search_text is not None:
        _dbq = _dbq.join(
            models.Seller
        ).filter(or_(
            models.Seller.name.ilike(f"%{search_text}%"),
            models.SellerItems.notes.ilike(f"%{search_text}%"),
        ))

    return _dbq.order_by(desc(models.SellerItems.purchase_date)).offset(skip).limit(limit).all()


def get_sellers_items_list(
        db: Session,
        item_id: int, category_id: int,
        seller_id: int, ea_id: int,
        since: str, until: str,
        tid: int, search_text: str,
        skip: int = 0, limit: int = 1000
) -> List[models.SellerItems]:
    if tid:
        return [get_seller_item_by_id(db, tid=tid)]

    _dbq = db.query(models.SellerItems).join(models.Item).join(models.Seller)

    if since:
        _dbq = _dbq.filter(models.SellerItems.purchase_date >= since)
    if until:
        _dbq = _dbq.filter(models.SellerItems.purchase_date <= until)
    if item_id:
        _dbq = _dbq.filter(models.SellerItems.item_id == item_id)
    if seller_id:
        _dbq = _dbq.filter(models.SellerItems.seller_id == seller_id)
    if ea_id:
        _dbq = _dbq.filter(models.SellerItems.ea_id == ea_id)
    if category_id:
        _dbq = _dbq.filter(models.Item.category_id == category_id)

    if search_text is not None:
        _dbq = _dbq.filter(or_(
            models.Seller.name.ilike(f"%{search_text}%"),
            models.SellerItems.notes.ilike(f"%{search_text}%"),
            models.Item.name.ilike(f"%{search_text}%"),
            models.Item.notes.ilike(f"%{search_text}%"),
        ))

    return _dbq.order_by(desc(models.SellerItems.purchase_date)).offset(skip).limit(limit).all()


def get_seller_item_by_id(db: Session, tid: int) -> models.SellerItems:
    db_seller_item = db.get(models.SellerItems, tid)
    if db_seller_item is None:
        raise HTTPException(status_code=404, detail=f"Seller Item {tid} not found")
    return db_seller_item


def get_seller_item(db: Session, tid: int) -> models.SellerItems:
    return get_seller_item_by_id(db, tid)


def update_seller_item(db: Session, db_seller_item: models.SellerItems, seller_item_update: schemas.SellerItemsUpdate) -> models.SellerItems:
    old_ea_id = db_seller_item.ea_id
    old_seller_id = db_seller_item.seller_id
    old_item_id = db_seller_item.item_id

    db_seller_item.row_update_time = get_now()
    update_data = seller_item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_seller_item, key, value)

    try:
        db.add(db_seller_item)
        db.commit()

        if "ea_id" in update_data and update_data["ea_id"] != old_ea_id:
            update_expense_account_stats(db, old_ea_id)
        if "seller_id" in update_data and update_data["seller_id"] != old_seller_id:
            update_seller_stats(db, old_seller_id)
        if "item_id" in update_data and update_data["item_id"] != old_item_id:
            _update_item_and_category_stats(db, old_item_id)

        update_expense_account_stats(db, db_seller_item.ea_id)
        update_seller_stats(db, db_seller_item.seller_id)
        _update_item_and_category_stats(db, db_seller_item.item_id)
    except:
        db.rollback()
        raise

    db.refresh(db_seller_item)
    return db_seller_item


# ----------------------------------------------------------


def create_member_item(db: Session, item_id: int, member_item_create: schemas.MemberItemsCreate) -> models.MemberItems:
    db_member_item = models.MemberItems(item_id=item_id, **member_item_create.model_dump())
    db_member_item.row_update_time = get_now()
    try:
        db.add(db_member_item)
        db.commit()

        _update_item_and_category_stats(db, db_member_item.item_id)
        update_member_stats(db, db_member_item.member_id)
    except:
        db.rollback()
        raise

    db.refresh(db_member_item)
    return db_member_item


def get_item_members_list(db: Session, item_id: int, skip: int, limit: int, search_text: str) -> List[models.MemberItems]:
    _dbq = db.query(models.MemberItems).filter_by(item_id=item_id)

    if search_text is not None:
        _dbq = _dbq.join(
            models.Member
        ).filter(or_(
            models.Member.name.ilike(f"%{search_text}%"),
            models.MemberItems.notes.ilike(f"%{search_text}%"),
        ))

    return _dbq.order_by(desc(models.MemberItems.purchase_date)).offset(skip).limit(limit).all()


def get_members_items_list(
        db: Session,
        item_id: int, category_id: int,
        member_id: int,
        since: str, until: str,
        tid: int, search_text: str,
        skip: int = 0, limit: int = 1000
) -> List[models.MemberItems]:
    if tid:
        return [get_member_item_by_id(db, tid=tid)]

    _dbq = db.query(models.MemberItems).join(models.Item).join(models.Member)

    if since:
        _dbq = _dbq.filter(models.MemberItems.purchase_date >= since)
    if until:
        _dbq = _dbq.filter(models.MemberItems.purchase_date <= until)
    if item_id:
        _dbq = _dbq.filter(models.MemberItems.item_id == item_id)
    if member_id:
        _dbq = _dbq.filter(models.MemberItems.member_id == member_id)
    if category_id:
        _dbq = _dbq.filter(models.Item.category_id == category_id)

    if search_text is not None:
        _dbq = _dbq.filter(or_(
            models.Member.name.ilike(f"%{search_text}%"),
            models.MemberItems.notes.ilike(f"%{search_text}%"),
            models.Item.name.ilike(f"%{search_text}%"),
            models.Item.notes.ilike(f"%{search_text}%"),
        ))

    return _dbq.order_by(desc(models.MemberItems.purchase_date)).offset(skip).limit(limit).all()


def get_member_item_by_id(db: Session, tid: int) -> models.MemberItems:
    db_member_item = db.get(models.MemberItems, tid)
    if db_member_item is None:
        raise HTTPException(status_code=404, detail=f"Member Item {tid} not found")
    return db_member_item


def get_member_item(db: Session, tid: int) -> models.MemberItems:
    return get_member_item_by_id(db, tid)


def update_member_item(db: Session, db_member_item: models.MemberItems, member_item_update: schemas.MemberItemsUpdate) -> models.MemberItems:
    old_item_id = db_member_item.item_id
    old_member_id = db_member_item.member_id

    db_member_item.row_update_time = get_now()
    update_data = member_item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_member_item, key, value)

    try:
        db.add(db_member_item)
        db.commit()

        if "member_id" in update_data and update_data["member_id"] != old_member_id:
            update_member_stats(db, old_member_id)
        if "item_id" in update_data and update_data["item_id"] != old_item_id:
            _update_item_and_category_stats(db, old_item_id)
        _update_item_and_category_stats(db, db_member_item.item_id)
        update_member_stats(db, db_member_item.member_id)
    except:
        db.rollback()
        raise

    db.refresh(db_member_item)
    return db_member_item

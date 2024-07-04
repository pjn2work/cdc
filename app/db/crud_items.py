from typing import List

from sqlalchemy.orm import Session

from . import models, schemas


def create_item(db: Session, item_create: schemas.items.ItemCreate) -> models.Item:
    return None


def get_items_list(db: Session, skip: int, limit: int, search_text: str) -> List[models.Item]:
    return None


def get_item(db: Session, item_id: int) -> models.Item:
    return None


def get_item_by_id(db: Session, item_id: int) -> models.Item:
    return None


def update_item(db: Session, db_item: models.Item, item_update: schemas.items.ItemUpdate) -> models.Item:
    return None


# ----------------------------------------------------------


def create_category(db: Session, category_create: schemas.items.CategoryCreate) -> models.Category:
    return None


def get_categories_list(db: Session, skip: int, limit: int, search_text: str) -> List[models.Category]:
    return None


def get_category(db: Session, category_id: int) -> models.Category:
    return None


def get_category_by_id(db: Session, category_id: int) -> models.Category:
    return None


def update_category(db: Session, db_category: models.Category, category_update: schemas.items.CategoryUpdate) -> models.Category:
    return None


# ----------------------------------------------------------


def create_seller_item(db: Session, seller_item_create: schemas.seller_items.SellerItemsCreate) -> models.SellerItems:
    return None


def get_seller_items_list(db: Session, skip: int, limit: int, search_text: str) -> List[models.SellerItems]:
    return None


def get_seller_item(db: Session, tid: int) -> models.SellerItems:
    return None


def get_seller_item_by_id(db: Session, tid: int) -> models.SellerItems:
    return None


def update_seller_item(db: Session, db_seller_item: models.SellerItems, seller_item_update: schemas.seller_items.SellerItemsUpdate) -> models.SellerItems:
    return None


# ----------------------------------------------------------


def create_member_item(db: Session, member_item_create: schemas.member_items.MemberItemsCreate) -> models.MemberItems:
    return None


def get_member_items_list(db: Session, skip: int, limit: int, search_text: str) -> List[models.MemberItems]:
    return None


def get_member_item(db: Session, tid: int) -> models.MemberItems:
    return None


def get_member_item_by_id(db: Session, tid: int) -> models.MemberItems:
    return None


def update_member_item(db: Session, db_member_item: models.MemberItems, member_item_update: schemas.member_items.MemberItemsUpdate) -> models.MemberItems:
    return None

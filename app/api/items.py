from typing import List

from fastapi import APIRouter
from sqlalchemy.orm import Session
from starlette import status

from ..db import crud_items, schemas, DB_SESSION

router = APIRouter()


@router.post(
    path="/",
    response_model=schemas.items.ItemView,
    status_code=status.HTTP_201_CREATED
)
def create_item(
        item_create: schemas.items.ItemCreate,
        db: Session = DB_SESSION):
    return crud_items.create_item(db=db, item_create=item_create)


@router.get(
    path="/",
    response_model=List[schemas.items.Item],
    status_code=status.HTTP_200_OK
)
def list_items(
        skip: int = 0, limit: int = 1000,
        search_text: str = "",
        db: Session = DB_SESSION):
    return crud_items.get_items_list(db, skip=skip, limit=limit, search_text=search_text)


@router.get(
    path="/{item_id}",
    response_model=schemas.items.ItemView,
    status_code=status.HTTP_200_OK
)
def get_item(item_id: int, db: Session = DB_SESSION):
    return crud_items.get_item(db, item_id=item_id)


@router.put(
    path="/{item_id}",
    response_model=schemas.items.ItemView,
    status_code = status.HTTP_200_OK
)
def update_item(
        item_id: int,
        item_update: schemas.items.ItemUpdate,
        db: Session = DB_SESSION):
    db_item = crud_items.get_item_by_id(db, item_id=item_id)
    return crud_items.update_item(db, db_item=db_item, item_update=item_update)


# ----------------------------------------------------------


@router.post(
    path="/categories",
    response_model=schemas.items.CategoryView,
    status_code=status.HTTP_201_CREATED
)
def create_category(
        category_create: schemas.items.CategoryCreate,
        db: Session = DB_SESSION):
    return crud_items.create_category(db=db, category_create=category_create)


@router.get(
    path="/categories",
    response_model=List[schemas.items.Category],
    status_code=status.HTTP_200_OK
)
def list_categories(
        skip: int = 0, limit: int = 1000,
        search_text: str = "",
        db: Session = DB_SESSION):
    return crud_items.get_categories_list(db, skip=skip, limit=limit, search_text=search_text)


@router.get(
    path="/categories/{category_id}",
    response_model=schemas.items.CategoryView,
    status_code=status.HTTP_200_OK
)
def get_category(category_id: int, db: Session = DB_SESSION):
    return crud_items.get_category(db, category_id=category_id)


@router.put(
    path="/categories/{category_id}",
    response_model=schemas.items.CategoryView,
    status_code = status.HTTP_200_OK
)
def update_category(
        category_id: int,
        category_update: schemas.items.CategoryUpdate,
        db: Session = DB_SESSION):
    db_category = crud_items.get_category_by_id(db, category_id=category_id)
    return crud_items.update_category(db, db_category=db_category, category_update=category_update)


# ----------------------------------------------------------


@router.post(
    path="/{item_id}/sellers",
    response_model=schemas.items.SellerItems,
    status_code=status.HTTP_201_CREATED
)
def create_seller_item(
        seller_item_create: schemas.seller_items.SellerItemsCreate,
        db: Session = DB_SESSION):
    return crud_items.create_seller_item(db=db, seller_item_create=seller_item_create)


@router.get(
    path="/{item_id}/sellers",
    response_model=List[schemas.seller_items.SellerItems],
    status_code=status.HTTP_200_OK
)
def list_seller_items(
        skip: int = 0, limit: int = 1000,
        search_text: str = "",
        db: Session = DB_SESSION):
    return crud_items.get_seller_items_list(db, skip=skip, limit=limit, search_text=search_text)


@router.get(
    path="/sellers/{tid}",
    response_model=schemas.seller_items.SellerItems,
    status_code=status.HTTP_200_OK
)
def get_seller_item(tid: int, db: Session = DB_SESSION):
    return crud_items.get_seller_item(db, tid=tid)


@router.put(
    path="/sellers/{tid}",
    response_model=schemas.seller_items.SellerItems,
    status_code = status.HTTP_200_OK
)
def update_seller_item(
        tid: int,
        seller_item_update: schemas.seller_items.SellerItemsUpdate,
        db: Session = DB_SESSION):
    db_seller_item = crud_items.get_seller_item_by_id(db, tid=tid)
    return crud_items.update_seller_item(db, db_seller_item=db_seller_item, seller_item_update=seller_item_update)


# ----------------------------------------------------------


@router.post(
    path="/{item_id}/members",
    response_model=schemas.items.MemberItems,
    status_code=status.HTTP_201_CREATED
)
def create_member_item(
        member_item_create: schemas.member_items.MemberItemsCreate,
        db: Session = DB_SESSION):
    return crud_items.create_member_item(db=db, member_item_create=member_item_create)


@router.get(
    path="/{item_id}/members",
    response_model=List[schemas.member_items.MemberItems],
    status_code=status.HTTP_200_OK
)
def list_member_items(
        skip: int = 0, limit: int = 1000,
        search_text: str = "",
        db: Session = DB_SESSION):
    return crud_items.get_member_items_list(db, skip=skip, limit=limit, search_text=search_text)


@router.get(
    path="/members/{tid}",
    response_model=schemas.member_items.MemberItems,
    status_code=status.HTTP_200_OK
)
def get_member_item(tid: int, db: Session = DB_SESSION):
    return crud_items.get_member_item(db, tid=tid)


@router.put(
    path="/members/{tid}",
    response_model=schemas.member_items.MemberItems,
    status_code = status.HTTP_200_OK
)
def update_member_item(
        tid: int,
        member_item_update: schemas.member_items.MemberItemsUpdate,
        db: Session = DB_SESSION):
    db_member_item = crud_items.get_member_item_by_id(db, tid=tid)
    return crud_items.update_member_item(db, db_member_item=db_member_item, member_item_update=member_item_update)
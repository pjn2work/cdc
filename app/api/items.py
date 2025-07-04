from typing import List

from fastapi import APIRouter
from sqlalchemy.orm import Session
from starlette import status

from app.api import error_json
from app.db import crud_items, schemas, DB_SESSION
from app.sec import GET_CURRENT_API_CLIENT, TokenData, are_valid_scopes
from app.utils.errors import CustomException

router = APIRouter()


@router.post(
    path="/categories",
    response_model=schemas.CategoryView,
    status_code=status.HTTP_201_CREATED
)
def create_category(
        category_create: schemas.CategoryCreate,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:create", "category:create"], current_client)
    return crud_items.create_category(db=db, category_create=category_create)


@router.get(
    path="/categories",
    response_model=List[schemas.Category],
    status_code=status.HTTP_200_OK
)
def list_categories(
        skip: int = 0, limit: int = 1000,
        search_text: str = "",
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:read", "category:read"], current_client)

    try:
        return crud_items.get_categories_list(db, skip=skip, limit=limit, search_text=search_text)
    except CustomException as exc:
        return error_json(exc)


@router.get(
    path="/categories/{category_id}",
    response_model=schemas.CategoryView,
    status_code=status.HTTP_200_OK
)
def get_category(
        category_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:read", "category:read"], current_client)

    try:
        return crud_items.get_category(db, category_id=category_id)
    except CustomException as exc:
        return error_json(exc)


@router.put(
    path="/categories/{category_id}",
    response_model=schemas.CategoryView,
    status_code = status.HTTP_200_OK
)
def update_category(
        category_id: int,
        category_update: schemas.CategoryUpdate,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:update", "category:update"], current_client)

    try:
        db_category = crud_items.get_category_by_id(db, category_id=category_id)
        return crud_items.update_category(db, db_category=db_category, category_update=category_update)
    except CustomException as exc:
        return error_json(exc)


@router.delete(
    path="/categories/{category_id}",
    response_model=None,
    status_code=status.HTTP_200_OK
)
def delete_category(
        category_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:delete", "category:delete"], current_client)

    try:
        return crud_items.delete_category_by_id(db, category_id=category_id)
    except CustomException as exc:
        return error_json(exc)


# ----------------------------------------------------------


@router.post(
    path="/",
    response_model=schemas.ItemView,
    status_code=status.HTTP_201_CREATED
)
def create_item(
        item_create: schemas.ItemCreate,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:create", "item:create"], current_client)
    return crud_items.create_item(db=db, item_create=item_create)


@router.get(
    path="/",
    response_model=List[schemas.Item],
    status_code=status.HTTP_200_OK
)
def list_items(
        skip: int = 0, limit: int = 1000,
        search_text: str = "",
        category_id: int = 0,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:read", "item:read"], current_client)
    return crud_items.get_items_list(db, skip=skip, limit=limit, search_text=search_text, category_id=category_id)


@router.get(
    path="/{item_id}",
    response_model=schemas.ItemView,
    status_code=status.HTTP_200_OK
)
def get_item(
        item_id: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:read", "item:read"], current_client)

    try:
        return crud_items.get_item(db, item_id=item_id)
    except CustomException as exc:
        return error_json(exc)


@router.put(
    path="/{item_id}",
    response_model=schemas.ItemView,
    status_code = status.HTTP_200_OK
)
def update_item(
        item_id: int,
        item_update: schemas.ItemUpdate,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:update", "item:update"], current_client)

    try:
        db_item = crud_items.get_item_by_id(db, item_id=item_id)
        return crud_items.update_item(db, db_item=db_item, item_update=item_update)
    except CustomException as exc:
        return error_json(exc)


# ----------------------------------------------------------


@router.post(
    path="/{item_id}/sellers",
    response_model=schemas.SellerItems,
    status_code=status.HTTP_201_CREATED
)
def create_item_seller(
        item_id: int,
        seller_item_create: schemas.SellerItemsCreate,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:create", "seller_item:create"], current_client)
    return crud_items.create_seller_item(db=db, item_id=item_id, seller_item_create=seller_item_create)


@router.get(
    path="/{item_id}/sellers",
    response_model=List[schemas.SellerItems],
    status_code=status.HTTP_200_OK
)
def list_item_sellers(
        item_id: int,
        skip: int = 0, limit: int = 1000,
        search_text: str = "",
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:read", "seller_item:read"], current_client)
    return crud_items.get_item_sellers_list(db, item_id=item_id, skip=skip, limit=limit, search_text=search_text)


@router.get(
    path="/sellers/{tid}",
    response_model=schemas.SellerItems,
    status_code=status.HTTP_200_OK
)
def get_item_seller(
        tid: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:read", "seller_item:read"], current_client)

    try:
        return crud_items.get_seller_item(db, tid=tid)
    except CustomException as exc:
        return error_json(exc)


@router.put(
    path="/sellers/{tid}",
    response_model=schemas.SellerItems,
    status_code = status.HTTP_200_OK
)
def update_item_seller(
        tid: int,
        seller_item_update: schemas.SellerItemsUpdate,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:update", "seller_item:update"], current_client)

    try:
        db_seller_item = crud_items.get_seller_item_by_id(db, tid=tid)
        return crud_items.update_seller_item(db, db_seller_item=db_seller_item, seller_item_update=seller_item_update)
    except CustomException as exc:
        return error_json(exc)


# ----------------------------------------------------------


@router.post(
    path="/{item_id}/members",
    response_model=schemas.MemberItems,
    status_code=status.HTTP_201_CREATED
)
def create_item_member(
        item_id: int,
        member_item_create: schemas.MemberItemsCreate,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:create", "member_item:create"], current_client)
    return crud_items.create_member_item(db=db, item_id=item_id, member_item_create=member_item_create)


@router.get(
    path="/{item_id}/members",
    response_model=List[schemas.MemberItems],
    status_code=status.HTTP_200_OK
)
def list_item_members(
        item_id: int,
        skip: int = 0, limit: int = 1000,
        search_text: str = "",
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:read", "member_item:read"], current_client)

    try:
        return crud_items.get_item_members_list(db, item_id=item_id, skip=skip, limit=limit, search_text=search_text)
    except CustomException as exc:
        return error_json(exc)


@router.get(
    path="/members/{tid}",
    response_model=schemas.MemberItems,
    status_code=status.HTTP_200_OK
)
def get_item_member(
        tid: int,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:read", "member_item:read"], current_client)

    try:
        return crud_items.get_member_item(db, tid=tid)
    except CustomException as exc:
        return error_json(exc)


@router.put(
    path="/members/{tid}",
    response_model=schemas.MemberItems,
    status_code = status.HTTP_200_OK
)
def update_item_member(
        tid: int,
        member_item_update: schemas.MemberItemsUpdate,
        db: Session = DB_SESSION,
        current_client: TokenData = GET_CURRENT_API_CLIENT):
    are_valid_scopes(["app:update", "member_item:update"], current_client)

    try:
        db_member_item = crud_items.get_member_item_by_id(db, tid=tid)
        return crud_items.update_member_item(db, db_member_item=db_member_item, member_item_update=member_item_update)
    except CustomException as exc:
        return error_json(exc)

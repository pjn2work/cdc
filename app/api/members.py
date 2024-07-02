from typing import List
from fastapi import APIRouter
from sqlalchemy.orm import Session
from starlette import status

from ..db import crud_member, schemas, DB_SESSION


router = APIRouter()


@router.post(
    path="/",
    response_model=schemas.members.Member,
    status_code=status.HTTP_201_CREATED
)
def create_member(member: schemas.members.MemberCreate,
                  db: Session = DB_SESSION):
    return crud_member.create_member(db=db, member=member)


@router.get(
    path="/",
    response_model=List[schemas.members.Member],
    status_code=status.HTTP_200_OK
)
def list_members(skip: int = 0, limit: int = 1000,
                 only_due_missing: bool = None,
                 only_active_members: bool = None,
                 search_text: str = "",
                 db: Session = DB_SESSION):
    return crud_member.get_members_list(db, skip=skip, limit=limit, only_due_missing=only_due_missing, only_active_members=only_active_members, search_text=search_text)


@router.get(
    path="/{member_id}",
    response_model=schemas.members.MemberView,
    status_code=status.HTTP_200_OK
)
def get_member(member_id: int, db: Session = DB_SESSION):
    return crud_member.get_member(db, member_id=member_id)


@router.put(
    path="/{member_id}",
    response_model=schemas.members.Member,
    status_code = status.HTTP_200_OK
)
def update_member(member_id: int,
                  member_update: schemas.members.MemberUpdate,
                  db: Session = DB_SESSION):
    db_member = crud_member.get_member_by_id(db, member_id=member_id)
    return crud_member.update_member(db, db_member=db_member, member_update=member_update)


@router.put(
    path="/{member_id}/active",
    response_model=schemas.members.Member,
    status_code = status.HTTP_200_OK
)
def update_member_active(member_id: int,
                         member_update: schemas.members.MemberUpdateActive,
                         db: Session = DB_SESSION):
    db_member = crud_member.get_member_by_id(db, member_id=member_id)
    return crud_member.update_member_active(db, db_member=db_member, member_update=member_update)


@router.put(
    path="/{member_id}/amount",
    response_model=schemas.members.Member,
    status_code = status.HTTP_200_OK
)
def update_member_amount(member_id: int,
                         member_update: schemas.members.MemberUpdateAmount,
                         db: Session = DB_SESSION):
    db_member = crud_member.get_member_by_id(db, member_id=member_id)
    return crud_member.update_member_amount(db, db_member=db_member, member_update=member_update)

from typing import List, Optional

from pydantic import BaseModel, Field, EmailStr

from .seller_items import SellerItems


class SellerBase(BaseModel):
    name: str = Field(min_length=3, max_length=100, examples=["Pedro Nunes"])
    tlf: str = Field(min_length=9, max_length=13, examples=["912000678"])
    email: Optional[EmailStr] = Field(examples=["pedro@gmail.com"])
    notes: str = Field(default="", examples=["Book seller"])


class SellerCreate(SellerBase):
    pass


class SellerUpdate(BaseModel):
    name: Optional[str] = Field(min_length=3, max_length=100, default=None)
    tlf: Optional[str] = Field(min_length=9, max_length=13, default=None)
    email: Optional[EmailStr] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class Seller(SellerBase):
    seller_id: int

    seller_items: List[SellerItems] = []

    class Config:
        orm_mode: True

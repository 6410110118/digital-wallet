# Merchant
from typing import Optional , List
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, Relationship, SQLModel



from . import users

from .wallets import *


class BaseMerchant(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: Optional[str] = None
    tax_id: Optional[str] = None

    

class CreatedMerchant(BaseMerchant):
    pass

class UpdatedMerchant(BaseMerchant):
    pass

class Merchant(BaseMerchant):
    id: int
    user_id: int
    

class DBMerchant(BaseMerchant, SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    
    #wallets: list["wallets.DBWallet"] = Relationship(back_populates="merchant", cascade_delete=True)
    user_id: int = Field(default=None, foreign_key="users.id")
    user: users.DBUser | None = Relationship(back_populates="merchant")

class MerchantList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    merchants: list[Merchant]
    page: int
    page_size: int
    size_per_page: int

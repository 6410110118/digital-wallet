from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, Relationship, SQLModel


from .customers import DBCustomer
from .users import *
from . import merchants



class BaseWallet(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    balance: float
    

class CreatedWallet(BaseWallet):
    pass

class UpdatedWallet(BaseWallet):
    pass

class Wallet(BaseWallet):
    id: int
    balance: float
    user_id: int
    role: UserRole
    

class DBWallet(Wallet, SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    
    
    user : DBUser | None = Relationship(back_populates="wallets")
    user_id: int = Field(default=None, foreign_key="users.id")
    #customer_id: int = Field(default=None, foreign_key="customers.id" )
    #customer: Optional["DBCustomer"] = Relationship(back_populates="wallets")
    
    role: UserRole = Field(default=None)
    
class WalletList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    wallets: list[Wallet]
    page: int
    page_size: int
    size_per_page: int

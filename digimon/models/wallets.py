from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .users import DBUser
    from .items import DBItem

class BaseWallet(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: Optional[int] = None
    item_id: Optional[int] = None
    balance: float

class CreatedWallet(BaseWallet):
    pass

class UpdatedWallet(BaseWallet):
    pass

class Wallet(BaseWallet):
    id: int
    user_id: int
    item_id: int
    

class DBWallet(Wallet, SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    balance: float
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    user: Optional["DBUser"] = Relationship(back_populates="wallets")
    #item_id: Optional[int] = Field(default=None, foreign_key="items.id")
    #item: Optional["DBItem"] = Relationship(back_populates="wallet")

class WalletList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    wallets: list[Wallet]
    page: int
    page_size: int
    size_per_page: int

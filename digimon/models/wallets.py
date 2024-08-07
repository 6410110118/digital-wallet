#Base Models

# Wallet
from typing import Optional
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel


class BaseWallet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    balance : float

class CreatedWallet(BaseWallet):
    pass

class UpdatedWallet(BaseWallet):
    pass

class Wallet(BaseWallet):
    id: int



class DBWallet(Wallet, SQLModel , table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)

class WalletList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    wallets: list[Wallet]
    page: int
    page_size: int
    size_per_page: int

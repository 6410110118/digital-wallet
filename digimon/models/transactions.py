# Trasection
from typing import Optional
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel


class BaseTransaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    wallet_id: int
    merchant_id: int
    item_id: int
    amount:float

class CreatedTransaction(BaseTransaction):
    pass

class UpdatedTransaction(BaseTransaction):
    pass

class Transaction(BaseTransaction):
    id: int


class DBTransection(BaseTransaction, SQLModel , table=True):
    id: Optional[int] = Field(default=None, primary_key=True)



class TransactionList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    transactions: list[Transaction]
    page: int
    page_size: int
    size_per_page: int
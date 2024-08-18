# Trasection
from typing import Optional
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime

from .users import *
class BaseTransaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    item_id: int

    description: str | None = None

    
class CreatedTransaction(BaseTransaction):
    pass

class UpdatedTransaction(BaseTransaction):
    pass

class Transaction(BaseTransaction):
    id: int
    price: float
    merchant_id: int
    customer_id: int



class DBTransection(BaseTransaction, SQLModel , table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    price: float = Field(default=None)
    
    merchant_id: int = Field(default=None)
    
    customer_id: int = Field(default=None)





class TransactionList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    transactions: list[Transaction]
    page: int
    page_size: int
    size_per_page: int
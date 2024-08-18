from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from sqlmodel import Relationship, SQLModel, Field

from . import merchants
from .users import *
class BaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    
    
class CreatedItem(BaseItem):
    pass

class UpdatedItem(BaseItem):
    pass

class Item(BaseItem):
    id: int
    
    user_id: int
    role: UserRole

class DBItem(SQLModel, Item, table=True):
    __table_args__ = {'extend_existing': True}
    # Correctly define the primary key with default=None
    id: int = Field(default=None, primary_key=True)
    # Properly set foreign key reference
    #merchant_id: int = Field(default=None, foreign_key="dbmerchant.id")
    # Use proper type hints for relationship
    #merchant: merchants.DBMerchant | None = Relationship(back_populates="items")

    user_id: int = Field( default=None, foreign_key="users.id")
    user: DBUser | None = Relationship(back_populates="item")
    role: UserRole = Field(default=None)
class ItemList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[Item]
    page: int
    page_count: int
    
    size_per_page: int
    

# Import the BaseMerchant module correctly


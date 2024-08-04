from fastapi import FastAPI, HTTPException

from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select


#Base Models

# Wallet
class BaseWallet(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id : int
    balance : float

class CreatedWallet(BaseWallet):
    pass

class UpdatedWallet(BaseWallet):
    pass

class wallet(BaseWallet):
    id: int

# Item
class BaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str | None = None
    price: float
    tax: float | None = None

class CreatedItem(BaseItem):
    pass


class UpdatedItem(BaseItem):
    pass


class Item(BaseItem):
    id: int



# Merchant
class BaseMerchant(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: Optional[str] = None


class CreatedMerchant(BaseMerchant):
    pass

class UpdatedMerchant(BaseMerchant):
    pass

class merchant(BaseMerchant):
    id: int


# Trasection 
class BaseTransaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    wallet_id: int
    merchant_id: int
    item_id: int
    amount:float

class CreatedTransection(BaseTransection):
    pass

class UpdatedTransection(BaseTransection):
    pass

class Transection(BaseTransection):
    id: int




#Database Model

class DBWallet(BaseWallet, SQLModel , table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class DBItem(Item, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
class DBMerchant(BaseMerchant, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class DBTransection(BaseTransaction, SQLModel , table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

#WalletList

class walletList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    wallets: list[Wallet]
    page: int
    page_size: int
    size_per_page: int


# ItemList
class ItemList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[Item]
    page: int
    page_size: int
    size_per_page: int


# MerchantList
class MerchantList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    merchants: list[Merchant]
    page: int
    page_size: int
    size_per_page: int

# TransectionList

class TransactionList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    transactions: list[Transaction]
    page: int
    page_size: int
    size_per_page: int


connect_args = {}

engine = create_engine(
    "postgresql+pg8000://postgres:123456@localhost/digimon",
    echo=True,
    connect_args=connect_args,
)


SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()


# API endpoints

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/wallets")
async def create_wallet(wallet: BaseWallet):
    with Session(engine) as session:
        db_wallet = DBWallet(**wallet.dict())
        session.add(db_wallet)
        session.commit()
        session.refresh(db_wallet)
    return db_wallet

@app.get("/wallets/{wallet_id}")
async def read_wallet(wallet_id: int):
    with Session(engine) as session:
        wallet = session.get(DBWallet, wallet_id).all()
        if wallet:
            return wallet
    raise HTTPException(status_code=404, detail="Wallet not found")


@app.post("/items")
async def create_item(item: BaseItem):
    print("created_item", item)
    data = item.dict()
    dbitem = DBItem(**data)
    with Session(engine) as session:
        session.add(dbitem)
        session.commit()
        session.refresh(dbitem)

    # return Item.parse_obj(dbitem.dict())
    return Item.from_orm(dbitem)


@app.get("/items")
async def read_items() -> ItemList:
    with Session(engine) as session:
        items = session.exec(select(DBItem)).all()

    return ItemList.from_orm(dict(items=items, page_size=0, page=0, size_per_page=0))


@app.get("/items/{item_id}")
async def read_item(item_id: int) -> Item:
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        if db_item:
            return Item.from_orm(db_item)
    raise HTTPException(status_code=404, detail="Item not found")


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: UpdatedItem) -> Item:
    print("update_item", item)
    data = item.dict()
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        db_item.sqlmodel_update(data)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)

    # return Item.parse_obj(dbitem.dict())
    return Item.from_orm(db_item)


@app.delete("/items/{item_id}")
async def delete_item(item_id: int) -> dict:
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        session.delete(db_item)
        session.commit()

    return dict(message="delete success")


@app.post("/merchants")
async def create_merchant(merchant: BaseMerchant):
    with Session(engine) as session:
        db_merchant = DBMerchant(**merchant.dict())
        session.add(db_merchant)
        session.commit()
        session.refresh(db_merchant)
    return db_merchant

@app.get("/merchants/{merchant_id}")
async def read_merchant(merchant_id: int):
    with Session(engine) as session:
        merchant = session.get(DBMerchant, merchant_id).all()
        if merchant:
            return merchant
    raise HTTPException(status_code=404, detail="Merchant not found")

@app.post("/transection")
async def create_transection(transection: BaseTransaction):
    with Session(engine) as session:
        db_transection = DBTransection(**transection.dict())
        session.add(db_transection)
        session.commit()
        session.refresh(db_transection)

    return db_transection

@app.get("/transection/{transection_id}")
async def read_transection(transection_id: int):
    with Session(engine) as session:
        transection = session.get(DBTransection, transection_id).all()

        if transection:
            return transection
    raise HTTPException(status_code=404, detail="Transection not found")


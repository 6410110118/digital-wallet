from fastapi import FastAPI, HTTPException

from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, Relationship, SQLModel, create_engine, Session, select


#Base Models

# Wallet
class BaseWallet(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    balance : float

class CreatedWallet(BaseWallet):
    pass

class UpdatedWallet(BaseWallet):
    pass

class Wallet(BaseWallet):
    id: int

# Item
class BaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    merchant_id: int


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

class Merchant(BaseMerchant):
    id: int


# Trasection 
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




#Database Model

class DBWallet(Wallet, SQLModel , table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class DBItem(Item, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    merchant_id: Optional[int] = Field(default=None, foreign_key="dbmerchant.id")
    merchant: Optional["DBMerchant"] = Relationship(back_populates="items")
class DBMerchant(BaseMerchant, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    items: list["DBItem"] = Relationship(back_populates="merchant", cascade_delete=True)




class DBTransection(BaseTransaction, SQLModel , table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

#WalletList

class WalletList(BaseModel):
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
    "postgresql+pg8000://postgres:123456@localhost/digimondb",
    echo=True,
    connect_args=connect_args,
)

SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()


# API endpoints

@app.get("/")
def root():
    return {"message": "Hello World"}

# Wallet endpoints
@app.post("/wallets")
async def create_wallet(wallet: BaseWallet):
    with Session(engine) as session:
        db_wallet = DBWallet(**wallet.dict())
        session.add(db_wallet)
        session.commit()
        session.refresh(db_wallet)
    return db_wallet

@app.get("/wallets")
async def read_wallets() -> WalletList:
    with Session(engine) as session:
        wallets = session.exec(select(DBWallet)).all()
        return WalletList.from_orm(dict(wallets=wallets, page_size=0, page=0, size_per_page=0))

@app.get("/wallets/{wallet_id}")
async def read_wallet(wallet_id: int):
    with Session(engine) as session:
        wallet = session.get(DBWallet, wallet_id)
        if wallet:
            return wallet
    raise HTTPException(status_code=404, detail="Wallet not found")

@app.put("/wallets/{wallet_id}")

async def update_wallet(wallet_id: int, wallet: UpdatedWallet) -> Wallet:
    print("update_wallet", wallet)
    data = wallet.dict()
    with Session(engine) as session:
        db_wallet = session.get(DBWallet, wallet_id)
        db_wallet.update_from_dict(data)
        session.commit()
        session.refresh(db_wallet)
    return Wallet.from_orm(db_wallet)

@app.delete("/wallets/{wallet_id}")
async def delete_wallet(wallet_id:int) -> dict:
    with Session(engine) as sesion:
        db_wallet = sesion.get(DBWallet, wallet_id)
        sesion.delete(db_wallet)
        sesion.commit()
    return dict(massage="delete success")

################################################################

# Item Endpoints


@app.post("/items")
async def create_item(item: BaseItem):
    print("created_item", item)
    data = item.dict()
    dbitem = DBItem(**data)
    with Session(engine) as session:
        merchant = session.get(DBMerchant, item.merchant_id)
        if not merchant:
            raise HTTPException(status_code=404, detail="Merchant not found")
        session.add(dbitem)
        session.commit()
        session.refresh(dbitem)
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

########################################################################

# Merchant endpoints

@app.post("/merchants")
async def create_merchant(merchant: BaseMerchant):
    with Session(engine) as session:
        db_merchant = DBMerchant(**merchant.dict())
        session.add(db_merchant)
        session.commit()
        session.refresh(db_merchant)
    return db_merchant

@app.get("/merchants")
async def read_merchants() -> MerchantList:
    with Session(engine) as session:
        merchants = session.exec(select(DBMerchant)).all()
        return MerchantList.from_orm(dict(merchants=merchants, page_size=0, page=0, size_per_page=0))
    
@app.post("/merchants/{merchant_id}/items")
async def create_merchant_item(merchant_id: int, item: BaseItem):
    item.merchant_id = merchant_id
    return await create_item(item)

@app.put("/merchants/{merchant_id}")
async def update_merchant(merchant_id: int, merchant: UpdatedMerchant) -> Merchant:
    print("update_merchant", merchant)
    data = merchant.dict()
    with Session(engine) as session:
        db_merchant = session.get(DBMerchant, merchant_id)
        db_merchant.sqlmodel_update(data)
        session.add(db_merchant)
        session.commit()
        session.refresh(db_merchant)
    return Merchant.from_orm(db_merchant)

@app.delete("/merchants/{merchant_id}")
async def delete_merchant(merchant_id: int) -> dict:
    with Session(engine) as session:
        db_merchant = session.get(DBMerchant, merchant_id)
        session.delete(db_merchant)
        session.commit()
    return dict(message="delete success")


################################################################

# Transaction endpoints

@app.post("/transection")
async def create_transection(transection: BaseTransaction):
    with Session(engine) as session:
        db_transection = DBTransection(**transection.dict())
        session.add(db_transection)
        session.commit()
        session.refresh(db_transection)

    return db_transection


@app.get("/transections")
async def read_transections() -> TransactionList:
    with Session(engine) as session:
        transections = session.exec(select(DBTransection)).all()
        return TransactionList.from_orm(dict(transactions=transections, page_size=0, page=0, size_per_page=0))
    
@app.get("/transection/{transection_id}")
async def read_transection(transection_id: int):
    with Session(engine) as session:
        transection = session.get(DBTransection, transection_id).all()

        if transection:
            return transection
    raise HTTPException(status_code=404, detail="Transection not found")

@app.put("/transection/{transection_id}")

async def update_transection(transection_id: int, transection: UpdatedTransaction) -> Transaction: 
    print("update_transection", transection)
    data = transection.dict()
    with Session(engine) as session:
        db_transection = session.get(DBTransection, transection_id)
        db_transection.sqlmodel_update(data)
        session.add(db_transection)
        session.commit()
        session.refresh(db_transection)
    return Transaction.from_orm(db_transection)

@app.delete("/transection/{transection_id}")
async def delete_transection(transection_id: int) -> dict:
    with Session(engine) as session:
        db_transection = session.get(DBTransection, transection_id)
        session.delete(db_transection)
        session.commit()
    return dict(message="delete success")

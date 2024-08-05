from fastapi import APIRouter, HTTPException

from typing import Optional , List

from sqlmodel import Field, SQLModel, create_engine, Session, select

from models import BaseItem, engine
from models.items import DBItem, Item, ItemList , UpdatedItem
from models.merchants import DBMerchant

router = APIRouter(prefix="/items")
@router.post("/items")
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



@router.get("/items", response_model=ItemList)
async def read_items() -> ItemList:
    with Session(engine) as session:
        items = session.exec(select(DBItem)).all()
    return ItemList(items=items, page_size=0, page=0, size_per_page=0)



@router.get("/items/{item_id}")
async def read_item(item_id: int) -> Item:
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        if db_item:
            return Item.from_orm(db_item)
    raise HTTPException(status_code=404, detail="Item not found")


@router.put("/items/{item_id}")
async def update_item(item_id: int, item: UpdatedItem) -> Item:
    print("update_item", item)
    data = item.dict(exclude_unset=True)
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        for key, value in data.items():
            setattr(db_item, key, value)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
    return Item.from_orm(db_item)


@router.delete("/items/{item_id}")
async def delete_item(item_id: int) -> dict:
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        session.delete(db_item)
        session.commit()
    return {"message": "Item deleted successfully"}

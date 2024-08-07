from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Annotated
from sqlmodel import Field, SQLModel, select

from ..models import *
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter(prefix="/items")

async def get_session():
    async with AsyncSession(engine) as session:
        yield session

@router.post("")
async def create_item(item: Annotated[BaseItem, Depends()], session: Annotated[AsyncSession, Depends(get_session)]):
    print("created_item", item)
    data = item.dict()
    dbitem = DBItem(**data)
    merchant = await session.get(DBMerchant, item.merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    session.add(dbitem)
    await session.commit()
    await session.refresh(dbitem)
    return Item.from_orm(dbitem)

@router.get("", response_model=ItemList)
async def read_items(session: Annotated[AsyncSession, Depends(get_session)]) -> ItemList:
    result = await session.exec(select(DBItem))
    items = result.all()
    return ItemList(items=items, page_size=0, page=0, size_per_page=0)

@router.get("/{item_id}")
async def read_item(item_id: int, session: Annotated[AsyncSession, Depends(get_session)]) -> Item:
    db_item = await session.get(DBItem, item_id)
    if db_item:
        return Item.from_orm(db_item)
    raise HTTPException(status_code=404, detail="Item not found")

@router.put("/{item_id}")
async def update_item(item_id: int, item: Annotated[UpdatedItem, Depends()], session: Annotated[AsyncSession, Depends(get_session)]) -> Item:
    print("update_item", item)
    data = item.dict(exclude_unset=True)
    db_item = await session.get(DBItem, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in data.items():
        setattr(db_item, key, value)
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return Item.from_orm(db_item)

@router.delete("/{item_id}")
async def delete_item(item_id: int, session: Annotated[AsyncSession, Depends(get_session)]) -> dict:
    db_item = await session.get(DBItem, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    await session.delete(db_item)
    await session.commit()
    return {"message": "Item deleted successfully"}

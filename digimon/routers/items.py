import math
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Annotated
from sqlalchemy import func
from sqlmodel import Field, SQLModel, select

from .. import models
from .. import deps
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter(prefix="/items")



SIZE_PER_PAGE = 50


@router.get("")
async def read_items(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: int = 1,
) -> models.ItemList:

    result = await session.exec(
        select(models.DBItem).offset((page - 1) * SIZE_PER_PAGE).limit(SIZE_PER_PAGE)
    )
    items = result.all()

    page_count = int(
        math.ceil(
            (await session.exec(select(func.count(models.DBItem.id)))).first()
            / SIZE_PER_PAGE
        )
    )

    print("page_count", page_count)
    print("items", items)
    return models.ItemList.from_orm(
        dict(items=items, page_count=page_count, page=page, size_per_page=SIZE_PER_PAGE)
    )

@router.get("/{page_size}/")
async def read_items(
    page_size : int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: int = 1,
) -> models.ItemList:

    result = await session.exec(
        select(models.DBItem).offset((page - 1) * page_size).limit(page_size)
    )
    items = result.all()

    page_count = int(
        math.ceil(
            (await session.exec(select(func.count(models.DBItem.id)))).first()
            / page_size
        )
    )

    print("page_count", page_count)
    print("items", items)
    return models.ItemList.from_orm(
        dict(items=items, page_count=page_count, page=page, size_per_page=SIZE_PER_PAGE,page_size=page_size)
    )



@router.post("")
async def create_item(
    item: models.CreatedItem,

    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> models.Item | None:
    data = item.dict()
    dbitem = models.DBItem(**data)
    dbitem.user = current_user
    session.add(dbitem)
    await session.commit()
    await session.refresh(dbitem)

    return models.Item.from_orm(dbitem)


@router.get("/{item_id}")
async def read_item(item_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]) -> models.Item:
    db_item = await session.get(models.DBItem, item_id)
    if db_item:
        return models.Item.from_orm(db_item)
    raise HTTPException(status_code=404, detail="Item not found")

@router.put("/{item_id}")
async def update_item(item_id: int, item: Annotated[models.UpdatedItem, Depends()], session: Annotated[AsyncSession, Depends(models.get_session)]) -> models.Item:
    print("update_item", item)
    data = item.dict(exclude_unset=True)
    db_item = await session.get(models.DBItem, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in data.items():
        setattr(db_item, key, value)
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return models.Item.from_orm(db_item)

@router.delete("/{item_id}")
async def delete_item(item_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]) -> dict:
    db_item = await session.get(models.DBItem, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    await session.delete(db_item)
    await session.commit()
    return {"message": "Item deleted successfully"}

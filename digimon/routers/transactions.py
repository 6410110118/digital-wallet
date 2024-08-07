from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from ..models.transactions import BaseTransaction, DBTransection, TransactionList
from ..models import engine

router = APIRouter(prefix="/transections")

async def get_session():
    async with AsyncSession(engine) as session:
        yield session

@router.post("/transection")
async def create_transection(
    transection: Annotated[BaseTransaction, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    db_transection = DBTransection(**transection.dict())
    session.add(db_transection)
    await session.commit()
    await session.refresh(db_transection)
    return db_transection

@router.get("/transections")
async def read_transections(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> TransactionList:
    result = await session.exec(select(DBTransection))
    transections = result.all()
    return TransactionList.from_orm(dict(transactions=transections, page_size=0, page=0, size_per_page=0))

@router.get("/transection/{transection_id}")
async def read_transection(
    transection_id: int,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    transection = await session.get(DBTransection, transection_id)
    if transection:
        return transection
    raise HTTPException(status_code=404, detail="Transection not found")

@router.put("/transection/{transection_id}")
async def update_transection(
    transection_id: int,
    transection: Annotated[BaseTransaction, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)]
) -> DBTransection:
    print("update_transection", transection)
    data = transection.dict()
    db_transection = await session.get(DBTransection, transection_id)
    if db_transection is None:
        raise HTTPException(status_code=404, detail="Transection not found")
    for key, value in data.items():
        setattr(db_transection, key, value)
    session.add(db_transection)
    await session.commit()
    await session.refresh(db_transection)
    return db_transection

@router.delete("/transection/{transection_id}")
async def delete_transection(
    transection_id: int,
    session: Annotated[AsyncSession, Depends(get_session)]
) -> dict:
    db_transection = await session.get(DBTransection, transection_id)
    await session.delete(db_transection)
    await session.commit()
    return dict(message="delete success")

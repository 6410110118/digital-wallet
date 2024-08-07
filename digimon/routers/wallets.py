from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from ..models.wallets import BaseWallet, DBWallet, UpdatedWallet, Wallet, WalletList
from ..models import engine

router = APIRouter(prefix="/wallets")

async def get_session():
    async with AsyncSession(engine) as session:
        yield session

@router.post("/wallets")
async def create_wallet(
    wallet: Annotated[BaseWallet, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    db_wallet = DBWallet(**wallet.dict())
    session.add(db_wallet)
    await session.commit()
    await session.refresh(db_wallet)
    return db_wallet

@router.get("/wallets")
async def read_wallets(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> WalletList:
    result = await session.exec(select(DBWallet))
    wallets = result.all()
    return WalletList.from_orm(dict(wallets=wallets, page_size=0, page=0, size_per_page=0))

@router.get("/wallets/{wallet_id}")
async def read_wallet(
    wallet_id: int,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    wallet = await session.get(DBWallet, wallet_id)
    if wallet:
        return wallet
    raise HTTPException(status_code=404, detail="Wallet not found")

@router.put("/wallets/{wallet_id}")
async def update_wallet(
    wallet_id: int,
    wallet: Annotated[UpdatedWallet, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)]
) -> Wallet:
    print("update_wallet", wallet)
    data = wallet.dict()
    db_wallet = await session.get(DBWallet, wallet_id)
    db_wallet.update_from_dict(data)
    await session.commit()
    await session.refresh(db_wallet)
    return Wallet.from_orm(db_wallet)

@router.delete("/wallets/{wallet_id}")
async def delete_wallet(
    wallet_id: int,
    session: Annotated[AsyncSession, Depends(get_session)]
) -> dict:
    db_wallet = await session.get(DBWallet, wallet_id)
    await session.delete(db_wallet)
    await session.commit()
    return dict(message="delete success")

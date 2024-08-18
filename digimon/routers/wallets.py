from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from ..models.wallets import BaseWallet, DBWallet, UpdatedWallet, Wallet, WalletList
from ..models import engine
from .. import models
router = APIRouter(prefix="/wallets")


async def get_session():
    async with AsyncSession(engine) as session:
        yield session

# @router.post("")
# async def create_wallet(
#     wallet: models.CreatedWallet,
#     session: Annotated[AsyncSession, Depends(models.get_session)]
# )-> models.Wallet | None:
#     data = wallet.dict()
#     dbwallet= models.DBWallet(**data)
#     session.add(dbwallet)
#     await session.commit()
#     await session.refresh(dbwallet)

#     return models.Item.from_orm(dbwallet)
@router.get("")
async def read_wallets(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> WalletList:
    result = await session.exec(select(DBWallet))
    wallets = result.all()
    return WalletList.from_orm(dict(wallets=wallets, page_size=0, page=0, size_per_page=0))

@router.get("/{customer_id}")

async def get_wallet_by_customer_id(
    customer_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)]
) -> models.Wallet:
    result = await session.exec(select(DBWallet).where(DBWallet.user_id == customer_id))
    wallet = result.first()
    if wallet:
        return Wallet.from_orm(wallet)
    raise HTTPException(status_code=404, detail="Wallet not found")

@router.get("/{merchant_id}")

async def get_wallet_by_merchant_id(
    merchant_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)]
) -> models.Wallet:
    result = await session.exec(select(DBWallet).where(DBWallet.user_id == merchant_id))
    wallet = result.first()
    if wallet:
        return Wallet.from_orm(wallet)
    raise HTTPException(status_code=404, detail="Wallet not found")


@router.put("/{wallet_id}")
async def update_wallet(
    wallet_id: int,
    wallet: Annotated[UpdatedWallet, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)]
) -> Wallet :
    print("update_wallet", wallet)
    data = wallet.dict()
    db_wallet = await session.get(DBWallet, wallet_id)
    db_wallet.update_from_dict(data)
    await session.commit()
    await session.refresh(db_wallet)
    return Wallet.from_orm(db_wallet)

@router.delete("/{wallet_id}")
async def delete_wallet(
    wallet_id: int,
    session: Annotated[AsyncSession, Depends(get_session)]
) -> dict:
    db_wallet = await session.get(DBWallet, wallet_id)
    await session.delete(db_wallet)
    await session.commit()
    return dict(message="delete success")

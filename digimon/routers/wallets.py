from fastapi import APIRouter, HTTPException

from typing import Optional

from sqlmodel import Field, SQLModel, create_engine, Session, select

from models.wallets import BaseWallet, DBWallet, UpdatedWallet, Wallet, WalletList
from models import engine
 
router = APIRouter(prefix="/wallets")
@router.post("/wallets")
async def create_wallet(wallet: BaseWallet):
    with Session(engine) as session:
        db_wallet = DBWallet(**wallet.dict())
        session.add(db_wallet)
        session.commit()
        session.refresh(db_wallet)
    return db_wallet

@router.get("/wallets")
async def read_wallets() -> WalletList:
    with Session(engine) as session:
        wallets = session.exec(select(DBWallet)).all()
        return WalletList.from_orm(dict(wallets=wallets, page_size=0, page=0, size_per_page=0))

@router.get("/wallets/{wallet_id}")
async def read_wallet(wallet_id: int):
    with Session(engine) as session:
        wallet = session.get(DBWallet, wallet_id)
        if wallet:
            return wallet
    raise HTTPException(status_code=404, detail="Wallet not found")

@router.put("/wallets/{wallet_id}")
async def update_wallet(wallet_id: int, wallet: UpdatedWallet) -> Wallet:
    print("update_wallet", wallet)
    data = wallet.dict()
    with Session(engine) as session:
        db_wallet = session.get(DBWallet, wallet_id)
        db_wallet.update_from_dict(data)
        session.commit()
        session.refresh(db_wallet)
    return Wallet.from_orm(db_wallet)

@router.delete("/wallets/{wallet_id}")
async def delete_wallet(wallet_id:int) -> dict:
    with Session(engine) as sesion:
        db_wallet = sesion.get(DBWallet, wallet_id)
        sesion.delete(db_wallet)
        sesion.commit()
    return dict(massage="delete success")
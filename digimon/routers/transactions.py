from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from models.transactions import BaseTransaction, DBTransection, TransactionList

from models import engine
router = APIRouter(prefix="/transections")
@router.post("/transection")
async def create_transection(transection: BaseTransaction):
    with Session(engine) as session:
        db_transection = DBTransection(**transection.dict())
        session.add(db_transection)
        session.commit()
        session.refresh(db_transection)

    return db_transection


@router.get("/transections")
async def read_transections() -> TransactionList:
    with Session(engine) as session:
        transections = session.exec(select(DBTransection)).all()
        return TransactionList.from_orm(dict(transactions=transections, page_size=0, page=0, size_per_page=0))
    
@router.get("/transection/{transection_id}")
async def read_transection(transection_id: int):
    with Session(engine) as session:
        transection = session.get(DBTransection, transection_id).all()

        if transection:
            return transection
    raise HTTPException(status_code=404, detail="Transection not found")

@router.put("/transection/{transection_id}")
async def update_transection(transection_id: int, transection: BaseTransaction) -> DBTransection:
    print("update_transection", transection)
    data = transection.dict()
    with Session(engine) as session:
        db_transection = session.get(DBTransection, transection_id)
        if db_transection is None:
            raise HTTPException(status_code=404, detail="Transection not found")
        for key, value in data.items():
            setattr(db_transection, key, value)
        session.add(db_transection)
        session.commit()
        session.refresh(db_transection)
    return db_transection
@router.delete("/transection/{transection_id}")
async def delete_transection(transection_id: int) -> dict:
    with Session(engine) as session:
        db_transection = session.get(DBTransection, transection_id)
        session.delete(db_transection)
        session.commit()
    return dict(message="delete success")
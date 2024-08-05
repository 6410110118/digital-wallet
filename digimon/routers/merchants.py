from fastapi import APIRouter
from sqlmodel import Session, select
from models import engine
from models.items import BaseItem
from models.merchants import BaseMerchant, DBMerchant, Merchant, MerchantList, UpdatedMerchant
from routers.items import create_item

router = APIRouter(prefix="/merchants")
@router.post("/merchants")
async def create_merchant(merchant: BaseMerchant):
    with Session(engine) as session:
        db_merchant = DBMerchant(**merchant.dict())
        session.add(db_merchant)
        session.commit()
        session.refresh(db_merchant)
    return db_merchant

@router.get("/merchants")
async def read_merchants() -> MerchantList:
    with Session(engine) as session:
        merchants = session.exec(select(DBMerchant)).all()
        return MerchantList.from_orm(dict(merchants=merchants, page_size=0, page=0, size_per_page=0))
    
@router.post("/merchants/{merchant_id}/items")
async def create_merchant_item(merchant_id: int, item: BaseItem):
    item.merchant_id = merchant_id
    return await create_item(item)

@router.put("/merchants/{merchant_id}")
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

@router.delete("/merchants/{merchant_id}")
async def delete_merchant(merchant_id: int) -> dict:
    with Session(engine) as session:
        db_merchant = session.get(DBMerchant, merchant_id)
        session.delete(db_merchant)
        session.commit()
    return dict(message="delete success")

from fastapi import APIRouter, HTTPException, Depends

from typing import Optional, Annotated
from sqlmodel import Field, SQLModel, create_engine, Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models.users import User

from ..models import (
    Merchant,
    CreatedMerchant,
    UpdatedMerchant,
    MerchantList,
    DBMerchant,
    engine,
    get_session,
)

router = APIRouter(prefix="/merchants")


from .. import deps

# @router.post("")
# async def create_merchant(
#     merchant: CreatedMerchant,
#     session: Annotated[AsyncSession, Depends(get_session)],
#     current_user: User = Depends(deps.get_current_user)
# ) -> Merchant:
#     print("create_merchant", merchant)
#     data = merchant.dict()
#     dbmerchant = DBMerchant(**data)
#     dbmerchant.user = current_user
#     session.add(dbmerchant)
#     await session.commit()
#     await session.refresh(dbmerchant)
#     return Merchant.from_orm(dbmerchant)




@router.get("")
async def read_merchants(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> MerchantList:
    result = await session.exec(select(DBMerchant))
    merchants = result.all()

    return MerchantList.from_orm(
        dict(merchants=merchants, page_size=0, page=0, size_per_page=0)
    )


@router.get("/{merchant_id}")
async def read_merchant(
    merchant_id: int, session: Annotated[AsyncSession, Depends(get_session)]
) -> Merchant:
    db_merchant = await session.get(DBMerchant, merchant_id)
    if db_merchant:
        return Merchant.from_orm(db_merchant)
    raise HTTPException(status_code=404, detail="Merchant not found")


@router.put("/{merchant_id}")
async def update_merchant(
    merchant_id: int,
    merchant: UpdatedMerchant,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Merchant:
    data = merchant.dict()
    db_merchant = await session.get(DBMerchant, merchant_id)
    db_merchant.sqlmodel_update(data)
    session.add(db_merchant)
    await session.commit()
    await session.refresh(db_merchant)

    return Merchant.from_orm(db_merchant)


import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from digimon import models

@pytest.mark.asyncio
async def test_read_wallets(client: AsyncClient, session: models.AsyncSession):
    # เรียกดูรายการ Wallets ทั้งหมด
    response = await client.get("/wallets")
    
    assert response.status_code == 200
    data = response.json()
    assert "wallets" in data
    assert isinstance(data["wallets"], list)

@pytest.mark.asyncio
async def test_get_wallet_by_customer_id(client: AsyncClient, session: models.AsyncSession, user1: models.DBUser):
    # เพิ่ม Wallet สำหรับทดสอบ
    wallet = models.DBWallet(user_id=user1.id, balance=1000)
    session.add(wallet)
    await session.commit()
    await session.refresh(wallet)
    
    # ทดสอบการเรียกดู Wallet ตาม customer_id
    response = await client.get(f"/wallets/{user1.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user1.id
    assert data["balance"] == 1000

@pytest.mark.asyncio
async def test_update_wallet(client: AsyncClient, session: models.AsyncSession, user1: models.DBUser):
    # เพิ่ม Wallet สำหรับทดสอบ
    wallet = models.DBWallet(user_id=user1.id, balance=1000)
    session.add(wallet)
    await session.commit()
    await session.refresh(wallet)
    
    # ทดสอบการอัปเดต Wallet
    update_data = {"balance": 2000}
    response = await client.put(f"/wallets/{wallet.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == 2000

@pytest.mark.asyncio
async def test_delete_wallet(client: AsyncClient, session: models.AsyncSession, user1: models.DBUser):
    # เพิ่ม Wallet สำหรับทดสอบ
    wallet = models.DBWallet(user_id=user1.id, balance=1000)
    session.add(wallet)
    await session.commit()
    await session.refresh(wallet)
    
    # ทดสอบการลบ Wallet
    response = await client.delete(f"/wallets/{wallet.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "delete success"

@pytest.mark.asyncio
async def test_add_balance(client: AsyncClient, session: models.AsyncSession, token_user1: models.Token):
    # เพิ่ม Wallet สำหรับทดสอบ
    wallet = models.DBWallet(user_id=token_user1.user_id, balance=1000)
    session.add(wallet)
    await session.commit()
    await session.refresh(wallet)
    
    # ทดสอบการเพิ่มยอดเงินใน Wallet
    add_balance_data = {"balance": 500}
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    response = await client.put("/wallets/add", json=add_balance_data, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == 1500

import pytest
from httpx import AsyncClient
from digimon import models

@pytest.mark.asyncio
async def test_buy_item_success(
    client: AsyncClient, 
    token_customer: models.Token, 
    item: models.DBItem,
    customer_wallet: models.DBWallet,
    merchant_wallet: models.DBWallet
):
    # ทดสอบการซื้อไอเท็มสำเร็จ
    headers = {"Authorization": f"{token_customer.token_type} {token_customer.access_token}"}
    payload = {"item_id": item.id}

    initial_customer_balance = customer_wallet.balance
    initial_merchant_balance = merchant_wallet.balance
    item_price = item.price

    response = await client.post("/buy", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["item_id"] == item.id
    assert data["price"] == item_price
    assert data["merchant_id"] == item.merchant_id

    # ตรวจสอบยอดคงเหลือของ customer และ merchant หลังจากซื้อไอเท็ม
    updated_customer_wallet = await client.get(f"/wallets/{customer_wallet.id}", headers=headers)
    updated_merchant_wallet = await client.get(f"/wallets/{merchant_wallet.id}", headers=headers)

    assert updated_customer_wallet.json()["balance"] == initial_customer_balance - item_price
    assert updated_merchant_wallet.json()["balance"] == initial_merchant_balance + item_price

@pytest.mark.asyncio
async def test_buy_item_not_customer(
    client: AsyncClient, 
    token_merchant: models.Token, 
    item: models.DBItem
):
    # ทดสอบการซื้อไอเท็มโดยผู้ที่ไม่ใช่ customer (เช่น merchant)
    headers = {"Authorization": f"{token_merchant.token_type} {token_merchant.access_token}"}
    payload = {"item_id": item.id}

    response = await client.post("/buy", json=payload, headers=headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Only customer can buy items."

@pytest.mark.asyncio
async def test_buy_item_not_enough_balance(
    client: AsyncClient, 
    token_customer: models.Token, 
    item: models.DBItem,
    customer_wallet: models.DBWallet
):
    # ทดสอบการซื้อไอเท็มเมื่อยอดคงเหลือไม่เพียงพอ
    headers = {"Authorization": f"{token_customer.token_type} {token_customer.access_token}"}
    payload = {"item_id": item.id}

    # ลดยอดคงเหลือของ customer ให้ต่ำกว่าราคาสินค้า
    customer_wallet.balance = 0.0

    response = await client.post("/buy", json=payload, headers=headers)

    assert response.status_code == 400  # กำหนด error code ตามความเหมาะสม
    assert response.json()["detail"] == "Not enough balance."


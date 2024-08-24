import pytest
from httpx import AsyncClient
from digimon import models

@pytest.mark.asyncio
async def test_read_items(client: AsyncClient, session: models.AsyncSession):
    # ทดสอบการเรียกดูรายการ Items ทั้งหมด
    response = await client.get("/items?page=1")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)

@pytest.mark.asyncio
async def test_create_item(client: AsyncClient, token_user1: models.Token, session: models.AsyncSession):
    # ทดสอบการสร้าง Item ใหม่
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = {
        "name": "Item Test",
        "description": "Item description",
        "price": 100.0
    }
    
    response = await client.post("/items", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["price"] == payload["price"]
    assert data["id"] > 0

@pytest.mark.asyncio
async def test_read_item(client: AsyncClient, session: models.AsyncSession, created_item: models.DBItem):
    # ทดสอบการเรียกดู Item ตาม ID
    response = await client.get(f"/items/{created_item.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_item.id
    assert data["name"] == created_item.name

@pytest.mark.asyncio
async def test_update_item(client: AsyncClient, token_user1: models.Token, created_item: models.DBItem):
    # ทดสอบการอัปเดต Item
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = {"name": "Updated Item Name"}
    
    response = await client.put(f"/items/{created_item.id}", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_item.id
    assert data["name"] == payload["name"]

@pytest.mark.asyncio
async def test_delete_item(client: AsyncClient, token_user1: models.Token, created_item: models.DBItem):
    # ทดสอบการลบ Item
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    
    response = await client.delete(f"/items/{created_item.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Item deleted successfully"

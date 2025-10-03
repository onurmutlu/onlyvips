"""
Pytest Configuration ve Test Fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.core.config import settings
from app.core.database import db
from app.utils.cache import cache


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Event loop fixture for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> TestClient:
    """Sync test client"""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
async def setup_test_environment():
    """Her test öncesi ve sonrası çalışan setup"""
    # Test öncesi
    settings.ENVIRONMENT = "test"
    settings.DB_PROVIDER = "memory"
    
    yield
    
    # Test sonrası temizlik
    try:
        # Cache temizle
        await cache.clear_pattern("*")
    except Exception:
        pass


@pytest.fixture
def mock_user_data():
    """Mock kullanıcı verisi"""
    return {
        "id": "test_user_123",
        "username": "testuser",
        "telegram_id": "123456789",
        "email": "test@example.com",
        "is_active": True,
        "is_premium": False,
        "created_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_content_data():
    """Mock içerik verisi"""
    return {
        "id": "content_123",
        "title": "Test Content",
        "description": "Test content description",
        "type": "image",
        "url": "https://example.com/image.jpg",
        "creator_id": "creator_123",
        "is_premium": False,
        "created_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_task_data():
    """Mock görev verisi"""
    return {
        "id": "task_123",
        "title": "Test Task",
        "description": "Complete this test task",
        "type": "social_media",
        "reward_xp": 100,
        "reward_tokens": 10,
        "requirements": {
            "action": "follow",
            "target": "@testaccount"
        },
        "is_active": True
    }


@pytest.fixture
def auth_headers(mock_user_data):
    """Authentication headers for tests"""
    # Mock JWT token (gerçek production'da kullanılmamalı)
    mock_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0X3VzZXJfMTIzIiwidXNlcl9pZCI6InRlc3RfdXNlcl8xMjMiLCJ1c2VybmFtZSI6InRlc3R1c2VyIiwiZXhwIjo5OTk5OTk5OTk5fQ.test"
    return {"Authorization": f"Bearer {mock_token}"}


@pytest.fixture
def mock_redis_client():
    """Mock Redis client"""
    class MockRedis:
        def __init__(self):
            self.data = {}
        
        async def get(self, key):
            return self.data.get(key)
        
        async def set(self, key, value):
            self.data[key] = value
            return True
        
        async def setex(self, key, ttl, value):
            self.data[key] = value
            return True
        
        async def delete(self, key):
            return self.data.pop(key, None) is not None
        
        async def exists(self, key):
            return key in self.data
        
        async def ping(self):
            return True
        
        async def close(self):
            pass
    
    return MockRedis()


@pytest.fixture
def mock_database():
    """Mock database"""
    class MockDB:
        def __init__(self):
            self.collections = {}
        
        def __getitem__(self, collection_name):
            if collection_name not in self.collections:
                self.collections[collection_name] = MockCollection()
            return self.collections[collection_name]
        
        async def command(self, command):
            if command == "ping":
                return {"ok": 1}
            return {}
    
    class MockCollection:
        def __init__(self):
            self.documents = []
        
        async def find_one(self, filter_dict):
            for doc in self.documents:
                if all(doc.get(k) == v for k, v in filter_dict.items()):
                    return doc
            return None
        
        async def find(self, filter_dict=None):
            if filter_dict is None:
                return self.documents
            return [doc for doc in self.documents 
                   if all(doc.get(k) == v for k, v in filter_dict.items())]
        
        async def insert_one(self, document):
            self.documents.append(document)
            return type('InsertResult', (), {'inserted_id': document.get('_id', 'mock_id')})()
        
        async def update_one(self, filter_dict, update_dict):
            for doc in self.documents:
                if all(doc.get(k) == v for k, v in filter_dict.items()):
                    doc.update(update_dict.get('$set', {}))
                    return type('UpdateResult', (), {'modified_count': 1})()
            return type('UpdateResult', (), {'modified_count': 0})()
        
        async def delete_one(self, filter_dict):
            for i, doc in enumerate(self.documents):
                if all(doc.get(k) == v for k, v in filter_dict.items()):
                    del self.documents[i]
                    return type('DeleteResult', (), {'deleted_count': 1})()
            return type('DeleteResult', (), {'deleted_count': 0})()
    
    return MockDB()


# Test utilities
class TestUtils:
    """Test yardımcı fonksiyonları"""
    
    @staticmethod
    def assert_response_success(response, expected_status=200):
        """Response başarılı mı kontrol et"""
        assert response.status_code == expected_status
        assert response.json() is not None
    
    @staticmethod
    def assert_response_error(response, expected_status=400):
        """Response hata mı kontrol et"""
        assert response.status_code == expected_status
        data = response.json()
        assert "detail" in data or "error" in data
    
    @staticmethod
    def assert_valid_user_data(user_data):
        """Kullanıcı verisi geçerli mi kontrol et"""
        required_fields = ["id", "username", "telegram_id"]
        for field in required_fields:
            assert field in user_data
            assert user_data[field] is not None
    
    @staticmethod
    def assert_valid_content_data(content_data):
        """İçerik verisi geçerli mi kontrol et"""
        required_fields = ["id", "title", "type", "creator_id"]
        for field in required_fields:
            assert field in content_data
            assert content_data[field] is not None


@pytest.fixture
def test_utils():
    """Test utilities fixture"""
    return TestUtils 
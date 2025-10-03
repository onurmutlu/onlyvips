"""
Health Endpoint Tests
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Health endpoint testleri"""
    
    def test_basic_health_check(self, client: TestClient):
        """Basit health check testi"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "service" in data
        assert "version" in data
        assert "environment" in data
    
    def test_root_endpoint(self, client: TestClient):
        """Root endpoint testi"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "service" in data
        assert "version" in data
        assert "status" in data
        assert "docs_url" in data
    
    @pytest.mark.asyncio
    async def test_detailed_health_check(self, async_client):
        """Detaylı health check testi"""
        response = await async_client.get("/api/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "total_check_time_ms" in data
        assert "checks" in data
        
        checks = data["checks"]
        assert "database" in checks
        assert "redis" in checks
        assert "external_services" in checks
    
    @pytest.mark.asyncio
    async def test_readiness_check(self, async_client):
        """Readiness probe testi"""
        response = await async_client.get("/api/health/readiness")
        
        # Memory database kullanıldığında başarılı olmalı
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ready"
        assert "timestamp" in data
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_liveness_check(self, async_client):
        """Liveness probe testi"""
        response = await async_client.get("/api/health/liveness")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "alive"
        assert "timestamp" in data
        assert "uptime_seconds" in data
        assert "message" in data 
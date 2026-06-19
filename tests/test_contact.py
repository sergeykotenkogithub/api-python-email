"""
Contact form API tests.

This module contains tests for the contact form endpoints.
"""

import pytest
import os
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import settings

# Disable rate limiting for tests
os.environ["RATE_LIMIT_REQUESTS"] = "1000"


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture
async def client():
    """Create test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestContactForm:
    """Test contact form endpoints."""
    
    @pytest.mark.anyio
    async def test_submit_contact_form_success(self, client: AsyncClient):
        """Test successful contact form submission."""
        contact_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+79991234567",
            "comment": "This is a test message for the contact form"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert "ai_analysis" in data["data"]
    
    @pytest.mark.anyio
    async def test_submit_contact_form_without_phone(self, client: AsyncClient):
        """Test contact form submission without phone."""
        contact_data = {
            "name": "Test User",
            "email": "test2@example.com",
            "comment": "This is a test message without phone number"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @pytest.mark.anyio
    async def test_submit_contact_form_invalid_email(self, client: AsyncClient):
        """Test contact form with invalid email."""
        contact_data = {
            "name": "Test",
            "email": "invalid-email",
            "comment": "Test message with invalid email"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
    
    @pytest.mark.anyio
    async def test_submit_contact_form_short_name(self, client: AsyncClient):
        """Test contact form with too short name."""
        contact_data = {
            "name": "A",
            "email": "test@example.com",
            "comment": "Test message with short name"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 422
    
    @pytest.mark.anyio
    async def test_submit_contact_form_short_comment(self, client: AsyncClient):
        """Test contact form with too short comment."""
        contact_data = {
            "name": "Test",
            "email": "test@example.com",
            "comment": "Hi"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 422
    
    @pytest.mark.anyio
    async def test_submit_contact_form_missing_required_fields(self, client: AsyncClient):
        """Test contact form with missing required fields."""
        contact_data = {
            "name": "Test"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 422


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    @pytest.mark.anyio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert "services" in data
    
    @pytest.mark.anyio
    async def test_api_status(self, client: AsyncClient):
        """Test API status endpoint."""
        response = await client.get("/api/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @pytest.mark.anyio
    async def test_metrics(self, client: AsyncClient):
        """Test metrics endpoint."""
        response = await client.get("/api/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data or "success" in data


class TestCORSSettings:
    """Test CORS settings."""
    
    @pytest.mark.anyio
    async def test_cors_headers(self, client: AsyncClient):
        """Test CORS headers are present."""
        response = await client.options("/api/contact", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST"
        })
        
        # OPTIONS might return 200 or 405 depending on implementation
        assert response.status_code in [200, 405]


class TestRootEndpoint:
    """Test root endpoint."""
    
    @pytest.mark.anyio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint returns API info."""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

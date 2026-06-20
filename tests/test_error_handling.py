"""
Error handling tests.

This module contains tests for error handling middleware and various error scenarios.
"""

import pytest
import os
from httpx import AsyncClient, ASGITransport
from app.main import app

# Disable rate limiting for tests
os.environ["RATE_LIMIT_REQUESTS"] = "10000"


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture
async def client():
    """Create test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestValidationError:
    """Test 422 Validation Error handling."""
    
    @pytest.mark.anyio
    async def test_invalid_email_format(self, client: AsyncClient):
        """Test validation error for invalid email format."""
        contact_data = {
            "name": "Test User",
            "email": "not-an-email",
            "comment": "This is a test message with invalid email"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "Validation Error"
        assert "details" in data
    
    @pytest.mark.anyio
    async def test_missing_required_fields(self, client: AsyncClient):
        """Test validation error for missing required fields."""
        contact_data = {
            "name": "Test"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "details" in data
    
    @pytest.mark.anyio
    async def test_name_too_short(self, client: AsyncClient):
        """Test validation error for name shorter than 2 characters."""
        contact_data = {
            "name": "A",
            "email": "test@example.com",
            "comment": "Valid comment text here"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 422
    
    @pytest.mark.anyio
    async def test_comment_too_short(self, client: AsyncClient):
        """Test validation error for comment shorter than 10 characters."""
        contact_data = {
            "name": "Test User",
            "email": "test@example.com",
            "comment": "Hi"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 422
    
    @pytest.mark.anyio
    async def test_comment_too_long(self, client: AsyncClient):
        """Test validation error for comment longer than 1000 characters."""
        contact_data = {
            "name": "Test User",
            "email": "test@example.com",
            "comment": "A" * 1001
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 422
    
    @pytest.mark.anyio
    async def test_invalid_json_body(self, client: AsyncClient):
        """Test error handling for invalid JSON body."""
        response = await client.post(
            "/api/contact",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        # Should return 422 or 400
        assert response.status_code in [400, 422, 500]


class TestPhoneValidation:
    """Test phone number validation errors."""
    
    @pytest.mark.anyio
    async def test_phone_with_letters(self, client: AsyncClient):
        """Test error when phone contains letters."""
        contact_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "hello123",
            "comment": "Test message with invalid phone"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
    
    @pytest.mark.anyio
    async def test_phone_too_short(self, client: AsyncClient):
        """Test error when phone has less than 10 digits."""
        contact_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+12345",
            "comment": "Test message with short phone"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 422
    
    @pytest.mark.anyio
    async def test_phone_too_long(self, client: AsyncClient):
        """Test error when phone has more than 15 digits."""
        contact_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890123456",
            "comment": "Test message with long phone"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 422
    
    @pytest.mark.anyio
    async def test_phone_plus_not_at_start(self, client: AsyncClient):
        """Test error when + is not at the beginning."""
        contact_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "7+9991234567",
            "comment": "Test message with invalid plus position"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 422
    
    @pytest.mark.anyio
    async def test_phone_multiple_plus_signs(self, client: AsyncClient):
        """Test error when phone has multiple + signs."""
        contact_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "++79991234567",
            "comment": "Test message with multiple plus signs"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 422
    
    @pytest.mark.anyio
    async def test_valid_phone_formats(self, client: AsyncClient):
        """Test various valid phone formats."""
        valid_phones = [
            "+79991234567",
            "79991234567",
            "+7 (999) 123-45-67",
            "+1-800-555-0199",
            "+44 20 7946 0958"
        ]
        
        for phone in valid_phones:
            contact_data = {
                "name": "Test User",
                "email": "test@example.com",
                "phone": phone,
                "comment": f"Test message with phone {phone}"
            }
            
            response = await client.post("/api/contact", json=contact_data)
            assert response.status_code == 200, f"Failed for phone: {phone}"


class TestNotFoundError:
    """Test 404 Not Found error handling."""
    
    @pytest.mark.anyio
    async def test_nonexistent_endpoint(self, client: AsyncClient):
        """Test 404 for nonexistent endpoint."""
        response = await client.get("/api/nonexistent")
        
        assert response.status_code == 404
    
    @pytest.mark.anyio
    async def test_wrong_http_method(self, client: AsyncClient):
        """Test error for wrong HTTP method."""
        response = await client.get("/api/contact")
        
        # Should return 405 Method Not Allowed
        assert response.status_code == 405


class TestErrorResponseFormat:
    """Test that error responses have correct format."""
    
    @pytest.mark.anyio
    async def test_validation_error_has_timestamp(self, client: AsyncClient):
        """Test that validation error includes timestamp."""
        contact_data = {
            "name": "Test",
            "email": "invalid",
            "comment": "Hi"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "timestamp" in data
    
    @pytest.mark.anyio
    async def test_validation_error_has_success_false(self, client: AsyncClient):
        """Test that validation error has success=False."""
        contact_data = {
            "name": "Test",
            "email": "invalid",
            "comment": "Hi"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        data = response.json()
        assert data["success"] is False
    
    @pytest.mark.anyio
    async def test_validation_error_has_error_field(self, client: AsyncClient):
        """Test that validation error includes error field."""
        contact_data = {
            "name": "Test",
            "email": "invalid",
            "comment": "Hi"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        data = response.json()
        assert "error" in data
        assert "message" in data


class TestNameValidation:
    """Test name validation."""
    
    @pytest.mark.anyio
    async def test_name_with_numbers(self, client: AsyncClient):
        """Test error when name contains numbers."""
        contact_data = {
            "name": "Test123",
            "email": "test@example.com",
            "comment": "Test message with numbers in name"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 422
    
    @pytest.mark.anyio
    async def test_name_with_special_chars(self, client: AsyncClient):
        """Test error when name contains special characters."""
        contact_data = {
            "name": "Test@#$%",
            "email": "test@example.com",
            "comment": "Test message with special chars in name"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 422
    
    @pytest.mark.anyio
    async def test_valid_cyrillic_name(self, client: AsyncClient):
        """Test that Cyrillic names are accepted."""
        contact_data = {
            "name": "Иван Иванов",
            "email": "test@example.com",
            "comment": "Тестовое сообщение на русском языке"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 200
    
    @pytest.mark.anyio
    async def test_valid_name_with_hyphen(self, client: AsyncClient):
        """Test that names with hyphens are accepted."""
        contact_data = {
            "name": "Анна-Мария",
            "email": "test@example.com",
            "comment": "Test message with hyphenated name"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 200


class TestXSSPrevention:
    """Test XSS prevention in input sanitization."""
    
    @pytest.mark.anyio
    async def test_script_tag_in_comment(self, client: AsyncClient):
        """Test that script tags are removed from comment."""
        contact_data = {
            "name": "Test User",
            "email": "test@example.com",
            "comment": "Hello <script>alert('xss')</script> world, this is a test message"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 200
        # The comment should be sanitized
        data = response.json()
        assert "<script>" not in str(data)
    
    @pytest.mark.anyio
    async def test_html_tags_in_comment(self, client: AsyncClient):
        """Test that HTML tags are removed from comment."""
        contact_data = {
            "name": "Test User",
            "email": "test@example.com",
            "comment": "Hello <b>bold</b> world, this is a test message"
        }
        
        response = await client.post("/api/contact", json=contact_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "<b>" not in str(data)
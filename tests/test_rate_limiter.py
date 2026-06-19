"""
Rate limiter tests.

This module contains tests for the rate limiting functionality.
"""

import pytest
import asyncio
import os
from app.repositories.rate_limiter import RateLimiter
from app.config import settings

# Set higher rate limit for tests
os.environ["RATE_LIMIT_REQUESTS"] = "100"


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture
def rate_limiter():
    """Create rate limiter instance."""
    return RateLimiter()


class TestRateLimiter:
    """Test rate limiter functionality."""
    
    @pytest.mark.anyio
    async def test_check_rate_limit_allows_first_request(self, rate_limiter: RateLimiter):
        """Test that first request is allowed."""
        client_id = "test_client_1"
        
        is_allowed, info = await rate_limiter.check_rate_limit(client_id)
        
        assert is_allowed is True
        assert info["allowed"] is True
    
    @pytest.mark.anyio
    async def test_check_rate_limit_tracks_requests(self, rate_limiter: RateLimiter):
        """Test that requests are tracked."""
        client_id = "test_client_2"
        
        # Make first request
        await rate_limiter.record_request(client_id)
        
        # Check rate limit
        is_allowed, info = await rate_limiter.check_rate_limit(client_id)
        
        assert is_allowed is True
    
    @pytest.mark.anyio
    async def test_rate_limit_exceeded(self, rate_limiter: RateLimiter):
        """Test rate limit exceeded behavior."""
        client_id = "test_client_3"
        
        # Make requests up to the limit
        for _ in range(settings.RATE_LIMIT_REQUESTS):
            await rate_limiter.record_request(client_id)
        
        # Next request should be blocked
        is_allowed, info = await rate_limiter.check_rate_limit(client_id)
        
        assert is_allowed is False
        assert info["allowed"] is False
        assert info["reason"] == "rate_limit_exceeded"
    
    @pytest.mark.anyio
    async def test_get_rate_limit_info(self, rate_limiter: RateLimiter):
        """Test getting rate limit info."""
        client_id = "test_client_4"
        
        # Make some requests
        await rate_limiter.record_request(client_id)
        await rate_limiter.record_request(client_id)
        
        info = await rate_limiter.get_rate_limit_info(client_id)
        
        assert info["limit"] == settings.RATE_LIMIT_REQUESTS
        assert info["current"] == 2
    
    @pytest.mark.anyio
    async def test_reset_rate_limit(self, rate_limiter: RateLimiter):
        """Test rate limit reset."""
        client_id = "test_client_5"
        
        # Make some requests
        await rate_limiter.record_request(client_id)
        await rate_limiter.record_request(client_id)
        
        # Reset rate limit
        await rate_limiter.reset_rate_limit(client_id)
        
        # Check that remaining is back to max
        info = await rate_limiter.get_rate_limit_info(client_id)
        
        assert info["current"] == 0
        assert info["remaining"] == settings.RATE_LIMIT_REQUESTS
    
    @pytest.mark.anyio
    async def test_different_clients_independent(self, rate_limiter: RateLimiter):
        """Test that different clients have independent rate limits."""
        client1 = "test_client_6"
        client2 = "test_client_7"
        
        # Exhaust client1's rate limit
        for _ in range(settings.RATE_LIMIT_REQUESTS):
            await rate_limiter.record_request(client1)
        
        # Client1 should be blocked
        is_allowed1, _ = await rate_limiter.check_rate_limit(client1)
        assert is_allowed1 is False
        
        # Client2 should still be allowed
        is_allowed2, _ = await rate_limiter.check_rate_limit(client2)
        assert is_allowed2 is True


class TestRateLimiterEdgeCases:
    """Test rate limiter edge cases."""
    
    @pytest.mark.anyio
    async def test_empty_client_id(self, rate_limiter: RateLimiter):
        """Test with empty client ID."""
        client_id = ""
        
        is_allowed, info = await rate_limiter.check_rate_limit(client_id)
        
        assert is_allowed is True
    
    @pytest.mark.anyio
    async def test_special_characters_in_client_id(self, rate_limiter: RateLimiter):
        """Test with special characters in client ID."""
        client_id = "test@client#123"
        
        is_allowed, info = await rate_limiter.check_rate_limit(client_id)
        
        assert is_allowed is True
    
    @pytest.mark.anyio
    async def test_concurrent_requests(self, rate_limiter: RateLimiter):
        """Test concurrent requests handling."""
        client_id = "test_client_concurrent"
        
        # Make concurrent requests
        tasks = [
            rate_limiter.record_request(client_id)
            for _ in range(5)
        ]
        
        await asyncio.gather(*tasks)
        
        info = await rate_limiter.get_rate_limit_info(client_id)
        
        assert info["current"] == 5
"""
Rate limiter module.

This module provides file-based rate limiting functionality
to protect against spam and abuse.
"""

import json
import aiofiles
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("RateLimiter")


class RateLimiter:
    """File-based rate limiter using sliding window algorithm."""
    
    def __init__(self):
        self.data_dir = Path(settings.DATA_DIR) / "rate_limits"
        self.max_requests = settings.RATE_LIMIT_REQUESTS
        self.window_seconds = settings.RATE_LIMIT_WINDOW
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Create rate limits directory if it doesn't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_client_file(self, client_id: str) -> Path:
        """Get the file path for a specific client."""
        # Sanitize client_id to prevent path traversal
        safe_id = "".join(c for c in client_id if c.isalnum() or c in "-_.")
        return self.data_dir / f"{safe_id}.json"
    
    async def _read_client_data(self, client_id: str) -> dict:
        """Read rate limit data for a client."""
        client_file = self._get_client_file(client_id)
        
        try:
            if not client_file.exists():
                return {"requests": [], "blocked_until": None}
            
            async with aiofiles.open(client_file, 'r') as f:
                content = await f.read()
                return json.loads(content) if content else {"requests": [], "blocked_until": None}
                
        except Exception as e:
            logger.error(f"Failed to read rate limit data for {client_id}: {e}")
            return {"requests": [], "blocked_until": None}
    
    async def _write_client_data(self, client_id: str, data: dict):
        """Write rate limit data for a client."""
        client_file = self._get_client_file(client_id)
        
        try:
            async with aiofiles.open(client_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
                
        except Exception as e:
            logger.error(f"Failed to write rate limit data for {client_id}: {e}")
            raise
    
    async def check_rate_limit(self, client_id: str) -> Tuple[bool, dict]:
        """Check if a client has exceeded the rate limit.
        
        Args:
            client_id: Unique identifier for the client (usually IP address)
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        now = datetime.utcnow()
        data = await self._read_client_data(client_id)
        
        # Check if client is currently blocked
        if data.get("blocked_until"):
            blocked_until = datetime.fromisoformat(data["blocked_until"])
            if now < blocked_until:
                remaining = (blocked_until - now).total_seconds()
                return False, {
                    "allowed": False,
                    "reason": "blocked",
                    "retry_after": int(remaining),
                    "limit": self.max_requests,
                    "window": self.window_seconds
                }
            else:
                # Block period expired, reset data
                data = {"requests": [], "blocked_until": None}
        
        # Clean up old requests outside the window
        window_start = now - timedelta(seconds=self.window_seconds)
        data["requests"] = [
            req_time for req_time in data["requests"]
            if datetime.fromisoformat(req_time) > window_start
        ]
        
        # Count requests in current window
        current_requests = len(data["requests"])
        
        if current_requests >= self.max_requests:
            # Block the client for the window duration
            blocked_until = now + timedelta(seconds=self.window_seconds)
            data["blocked_until"] = blocked_until.isoformat()
            await self._write_client_data(client_id, data)
            
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return False, {
                "allowed": False,
                "reason": "rate_limit_exceeded",
                "retry_after": self.window_seconds,
                "limit": self.max_requests,
                "window": self.window_seconds
            }
        
        # Request is allowed
        return True, {
            "allowed": True,
            "remaining": self.max_requests - current_requests - 1,
            "limit": self.max_requests,
            "window": self.window_seconds,
            "reset_time": (now + timedelta(seconds=self.window_seconds)).isoformat()
        }
    
    async def record_request(self, client_id: str):
        """Record a request for rate limiting purposes."""
        data = await self._read_client_data(client_id)
        now = datetime.utcnow()
        
        # Add current request timestamp
        data["requests"].append(now.isoformat())
        
        # Clean up old requests
        window_start = now - timedelta(seconds=self.window_seconds)
        data["requests"] = [
            req_time for req_time in data["requests"]
            if datetime.fromisoformat(req_time) > window_start
        ]
        
        await self._write_client_data(client_id, data)
    
    async def get_rate_limit_info(self, client_id: str) -> dict:
        """Get current rate limit information for a client."""
        data = await self._read_client_data(client_id)
        now = datetime.utcnow()
        
        # Clean up old requests
        window_start = now - timedelta(seconds=self.window_seconds)
        data["requests"] = [
            req_time for req_time in data["requests"]
            if datetime.fromisoformat(req_time) > window_start
        ]
        
        current_requests = len(data["requests"])
        
        return {
            "limit": self.max_requests,
            "remaining": max(0, self.max_requests - current_requests),
            "window": self.window_seconds,
            "current": current_requests,
            "reset_time": (now + timedelta(seconds=self.window_seconds)).isoformat()
        }
    
    async def reset_rate_limit(self, client_id: str):
        """Reset rate limit for a specific client."""
        data = {"requests": [], "blocked_until": None}
        await self._write_client_data(client_id, data)
        logger.info(f"Rate limit reset for client: {client_id}")
    
    async def cleanup_expired_entries(self):
        """Clean up expired rate limit entries."""
        try:
            now = datetime.utcnow()
            
            for client_file in self.data_dir.glob("*.json"):
                try:
                    async with aiofiles.open(client_file, 'r') as f:
                        content = await f.read()
                        data = json.loads(content) if content else {}
                    
                    # Check if block has expired
                    if data.get("blocked_until"):
                        blocked_until = datetime.fromisoformat(data["blocked_until"])
                        if now > blocked_until:
                            # Reset expired entry
                            await self._write_client_data(
                                client_file.stem, 
                                {"requests": [], "blocked_until": None}
                            )
                            
                except Exception as e:
                    logger.error(f"Failed to process rate limit file {client_file}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to cleanup rate limit entries: {e}")


# Create global rate limiter instance
rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Get rate limiter instance."""
    return rate_limiter
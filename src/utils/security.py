"""
Security Utilities

PURPOSE:
    Handles API security including API key validation and JWT token management.
    Ensures only authorized clients can access sensitive endpoints.

USAGE:
    from src.utils.security import verify_api_key
    # use as dependency in FastAPI
"""

import os
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from typing import Optional

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key_header: str = Security(api_key_header)):
    """
    Verify API Key from header
    
    Args:
        api_key_header: Key from request header
        
    Returns:
        Verified key
        
    Raises:
        HTTPException if invalid
    """
    # In production, fetch valid keys from DB/Secret Manager
    # This is a simplified check
    VALID_API_KEYS = os.getenv("VALID_CLIENT_KEYS", "test-client-key").split(",")
    
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key"
        )
        
    if api_key_header not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
        
    return api_key_header

def hash_password(password: str) -> str:
    """Hash a password (placeholder for bcrypt/argon2)"""
    # Use passlib in production
    return f"hashed_{password}"

__all__ = ['verify_api_key', 'hash_password']

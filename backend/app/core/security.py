"""
Security utilities (JWT, password hashing, encryption)
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import os
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

# JWT utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None

# Credential encryption/decryption
def get_cipher():
    """Get Fernet cipher for encryption"""
    # Ensure key is 32 bytes
    key = settings.SECRET_KEY.encode()[:32].ljust(32, b'0')
    # Fernet requires base64-encoded 32 bytes
    encoded_key = Fernet.generate_key()  # Will be replaced with proper key
    # For now, use a simple approach - proper implementation would use a secure key derivation
    return None

def encrypt_credentials(data: str) -> str:
    """Encrypt sensitive credentials"""
    # Placeholder - implement with proper encryption
    # In production, use a proper key management system
    return data

def decrypt_credentials(encrypted_data: str) -> str:
    """Decrypt sensitive credentials"""
    # Placeholder - implement with proper decryption
    return encrypted_data

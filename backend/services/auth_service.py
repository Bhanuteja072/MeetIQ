# backend/services/auth_service.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    """Turn 'mypassword' into '$2b$12$...' (bcrypt hash)"""
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    """Check if plain password matches stored hash"""
    return pwd_context.verify(plain, hashed)

def create_access_token(user_id: str, email: str) -> str:
    """
    Create a JWT token.
    Payload contains user_id + email + expiry time.
    Signed with JWT_SECRET_KEY so nobody can forge it.
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": user_id,        # subject = user_id
        "email": email,
        "exp": expire
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[dict]:
    """
    Verify + decode a JWT token.
    Returns payload dict or None if invalid/expired.
    """
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
    except JWTError:
        return None
    


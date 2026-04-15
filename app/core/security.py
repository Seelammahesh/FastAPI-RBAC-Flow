from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import Settings
import hashlib
import uuid

pwd_context =CryptContext(schemes=["bcrypt"],deprecated="auto")


def hash_password(password: str):
    # Fixed  bcrypt 72-byte limit
    password = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    plain = hashlib.sha256(plain.encode()).hexdigest()
    return pwd_context.verify(plain, hashed)


def create_access_token(data : dict):
    to_encode=data.copy()
    expire=datetime.utcnow() + timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire,"type":"access"})
    return jwt.encode(to_encode,Settings.SECRET_KEY,algorithm=Settings.ALGORITHM)


def create_refresh_token(data : dict):
    to_encode=data.copy()
    expire=datetime.utcnow() + timedelta(days=Settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp":expire,"type":"refresh"})
    return jwt.encode(to_encode,Settings.SECRET_KEY,algorithm=Settings.ALGORITHM)
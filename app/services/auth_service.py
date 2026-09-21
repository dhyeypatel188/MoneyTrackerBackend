"""
Auth service — password hashing (bcrypt) and JWT creation/verification.
Think of this as your NestJS JwtService + BcryptService combined.
"""
from datetime import datetime, timedelta, timezone
from typing import Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app import models

import bcrypt

# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Hash a plain-text password. Store this in the DB — never the plain one."""
    pwd_bytes = plain.encode("utf-8")[:72]
    return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Check if a plain-text password matches the stored hash."""
    try:
        pwd_bytes = plain.encode("utf-8")[:72]
        return bcrypt.checkpw(pwd_bytes, hashed.encode("utf-8"))
    except Exception:
        return False


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    """
    Create a signed JWT token.
    Same as jwtService.sign(payload) in NestJS.
    """
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload.update({"exp": expire})

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Union[dict, None]:
    """
    Decode and verify a JWT token.
    Returns the payload dict, or None if invalid/expired.
    """
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None


# ── User helpers ──────────────────────────────────────────────────────────────

def get_user_by_username(db: Session, username: str) -> Union[models.User, None]:
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, username: str, password: str) -> models.User:
    user = models.User(
        username=username,
        hashed_password=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> Union[models.User, None]:
    """
    Find user by username and verify password.
    Returns the User object if valid, None otherwise.
    Same as LocalStrategy.validate() in NestJS Passport.
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

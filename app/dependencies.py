"""
JWT dependency — inject into any route to protect it.
This is the FastAPI equivalent of NestJS @UseGuards(JwtAuthGuard).
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import auth_service
from app import models

# Reads the "Authorization: Bearer <token>" header automatically
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """
    FastAPI dependency that:
    1. Reads the Authorization: Bearer <token> header
    2. Decodes and validates the JWT
    3. Returns the logged-in User object

    Inject with:  current_user: User = Depends(get_current_user)
    Same as:      @UseGuards(JwtAuthGuard) in NestJS
    """
    token = credentials.credentials
    payload = auth_service.decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = auth_service.get_user_by_username(db, username)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user

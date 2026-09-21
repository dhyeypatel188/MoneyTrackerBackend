"""
Auth router — register and login endpoints.
NestJS equivalent: AuthController with /auth/register and /auth/login
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.services import auth_service
from app.dependencies import get_current_user
from app import models

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """
    Create a new user account.
    Equivalent to: POST /auth/register in NestJS
    """
    # Check if username already taken
    existing = auth_service.get_user_by_username(db, payload.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    user = auth_service.create_user(db, payload.username, payload.password)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with username + password → returns JWT access token.
    Equivalent to: POST /auth/login in NestJS Passport local strategy
    """
    user = auth_service.authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    token = auth_service.create_access_token(data={"sub": user.username})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    """
    Get the currently logged-in user's profile.
    Equivalent to: @UseGuards(JwtAuthGuard) + @Request() req in NestJS
    """
    return current_user

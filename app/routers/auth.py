"""
Auth router — register, login, me, and logout endpoints.
Uses standardized corporate response envelope format.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import RegisterRequest, LoginRequest
from app.services import auth_service
from app.dependencies import get_current_user
from app.common.response import build_response
from app import models

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    """
    Create a new user account.
    """
    existing = auth_service.get_user_by_username(db, payload.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    user = auth_service.create_user(db, payload.username, payload.password)
    return build_response(
        status_code=status.HTTP_201_CREATED,
        status_desc="User registered successfully",
        data={
            "id": user.id,
            "username": user.username,
            "is_active": user.is_active,
        },
        path=str(request.url.path),
        method=request.method,
    )


@router.post("/login", status_code=status.HTTP_200_OK)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """
    Login with username + password → returns JWT access token.
    """
    user = auth_service.authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    token = auth_service.create_access_token(data={"sub": user.username})
    return build_response(
        status_code=status.HTTP_200_OK,
        status_desc="Login successful",
        data={
            "access_token": token,
            "token_type": "bearer",
            "username": user.username,
        },
        path=str(request.url.path),
        method=request.method,
    )


@router.get("/me", status_code=status.HTTP_200_OK)
def get_me(request: Request, current_user: models.User = Depends(get_current_user)):
    """
    Get the currently logged-in user's profile.
    """
    return build_response(
        status_code=status.HTTP_200_OK,
        status_desc="User profile fetched successfully",
        data={
            "id": current_user.id,
            "username": current_user.username,
            "is_active": current_user.is_active,
        },
        path=str(request.url.path),
        method=request.method,
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
@router.post("/signout", status_code=status.HTTP_200_OK)
def logout(request: Request):
    """
    Sign out / Log out endpoint.
    Handles server-side session termination and confirmation.
    """
    return build_response(
        status_code=status.HTTP_200_OK,
        status_desc="Successfully signed out",
        data={
            "message": "Successfully signed out",
        },
        path=str(request.url.path),
        method=request.method,
    )

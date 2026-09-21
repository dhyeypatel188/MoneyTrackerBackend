from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ExpenseCreate, ExpenseResponse
from app.services import expense_service
from app.dependencies import get_current_user
from app import models

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseResponse, status_code=201)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),  # 🔒 JWT protected
):
    return expense_service.create_expense(db, payload)


@router.get("", response_model=list[ExpenseResponse])
def list_expenses(
    category: Optional[str] = Query(None, description="Filter by category (case-insensitive)"),
    from_date: Optional[date] = Query(None, description="Filter expenses on or after this date (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="Filter expenses on or before this date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),  # 🔒 JWT protected
):
    if from_date and to_date and from_date > to_date:
        raise HTTPException(status_code=400, detail="from_date must be before or equal to to_date")
    return expense_service.list_expenses(db, category=category, from_date=from_date, to_date=to_date)

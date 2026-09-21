from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ExpenseCreate, ExpenseResponse
from app.services import expense_service
from app.dependencies import get_current_user
from app.common.response import build_response
from app import models

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: ExpenseCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),  # 🔒 JWT protected
):
    expense = expense_service.create_expense(db, payload)
    data = ExpenseResponse.model_validate(expense).model_dump(mode="json")
    return build_response(
        status_code=status.HTTP_201_CREATED,
        status_desc="Expense created successfully",
        data=data,
        path=str(request.url.path),
        method=request.method,
    )


@router.get("", status_code=status.HTTP_200_OK)
def list_expenses(
    request: Request,
    category: Optional[str] = Query(None, description="Filter by category (case-insensitive)"),
    from_date: Optional[date] = Query(None, description="Filter expenses on or after this date (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="Filter expenses on or before this date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),  # 🔒 JWT protected
):
    if from_date and to_date and from_date > to_date:
        raise HTTPException(status_code=400, detail="from_date must be before or equal to to_date")
    expenses = expense_service.list_expenses(db, category=category, from_date=from_date, to_date=to_date)
    data = [ExpenseResponse.model_validate(e).model_dump(mode="json") for e in expenses]
    return build_response(
        status_code=status.HTTP_200_OK,
        status_desc="Expenses retrieved successfully",
        data=data,
        path=str(request.url.path),
        method=request.method,
    )

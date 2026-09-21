from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from app import models, schemas


def create_expense(db: Session, data: schemas.ExpenseCreate) -> models.Expense:
    expense = models.Expense(
        amount=data.amount,
        category=data.category.strip(),
        note=data.note,
        date=data.date if data.date is not None else date.today(),
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def list_expenses(
    db: Session,
    category: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> list[models.Expense]:
    query = db.query(models.Expense)

    if category:
        query = query.filter(models.Expense.category.ilike(category))
    if from_date:
        query = query.filter(models.Expense.date >= from_date)
    if to_date:
        query = query.filter(models.Expense.date <= to_date)

    return query.order_by(models.Expense.date.desc(), models.Expense.id.desc()).all()

from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas


def _spend_in_month(db: Session, year: int, month: int) -> dict[str, Decimal]:
    """Returns {category: total_amount} for a given year-month."""
    rows = (
        db.query(models.Expense.category, func.sum(models.Expense.amount))
        .filter(
            func.strftime("%Y", models.Expense.date) == str(year),
            func.strftime("%m", models.Expense.date) == f"{month:02d}",
        )
        .group_by(models.Expense.category)
        .all()
    )
    return {cat: Decimal(str(total)) for cat, total in rows}


def get_summary(db: Session) -> schemas.SummaryResponse:
    today = date.today()
    cur_year, cur_month = today.year, today.month

    # Previous month
    if cur_month == 1:
        prev_year, prev_month = cur_year - 1, 12
    else:
        prev_year, prev_month = cur_year, cur_month - 1

    current_by_cat = _spend_in_month(db, cur_year, cur_month)
    previous_by_cat = _spend_in_month(db, prev_year, prev_month)

    # All-time totals by category
    all_rows = (
        db.query(models.Expense.category, func.sum(models.Expense.amount))
        .group_by(models.Expense.category)
        .all()
    )
    by_category = {cat: Decimal(str(total)) for cat, total in all_rows}
    total_spend = sum(by_category.values(), Decimal("0"))

    # Month-over-month totals
    cur_total = sum(current_by_cat.values(), Decimal("0"))
    prev_total = sum(previous_by_cat.values(), Decimal("0"))

    if prev_total > 0:
        mom_change = float(((cur_total - prev_total) / prev_total) * 100)
    else:
        mom_change = None

    mom = schemas.MonthOverMonth(
        current_month=cur_total,
        previous_month=prev_total,
        change_percent=mom_change,
    )

    # Per-category insights (flag >20% increase)
    all_categories = set(current_by_cat) | set(previous_by_cat)
    insights: list[schemas.CategoryInsight] = []

    for cat in all_categories:
        cur = current_by_cat.get(cat, Decimal("0"))
        prev = previous_by_cat.get(cat, Decimal("0"))

        if prev > 0:
            pct = float(((cur - prev) / prev) * 100)
        elif cur > 0:
            pct = 100.0  # new category this month
        else:
            pct = 0.0

        insights.append(
            schemas.CategoryInsight(
                category=cat,
                current_month=cur,
                previous_month=prev,
                change_percent=round(pct, 2),
                flagged=pct > 20,
            )
        )

    insights.sort(key=lambda x: x.change_percent, reverse=True)

    return schemas.SummaryResponse(
        total_spend=total_spend,
        by_category=by_category,
        month_over_month=mom,
        insights=insights,
    )

from datetime import date, datetime
from decimal import Decimal
from typing import Union, Optional, Annotated
from pydantic import BaseModel, field_validator, ConfigDict, BeforeValidator


def _parse_date(v: object) -> object:
    """Accept ISO date strings, date objects, or None."""
    if v is None or isinstance(v, date):
        return v
    if isinstance(v, str):
        try:
            return datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid date format '{v}'. Expected YYYY-MM-DD.")
    raise ValueError(f"Cannot parse date from {type(v)}")


OptionalDate = Annotated[Optional[date], BeforeValidator(_parse_date)]


# ── Request schemas ──────────────────────────────────────────────────────────

class ExpenseCreate(BaseModel):
    amount: Decimal
    category: str
    note: Union[str, None] = None
    date: OptionalDate = None  # defaults to today in the service layer

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("amount must be greater than zero")
        return v

    @field_validator("category")
    @classmethod
    def category_must_not_be_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("category must not be blank")
        return v


# ── Response schemas ─────────────────────────────────────────────────────────

class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    category: str
    note: Union[str, None]
    date: date


# ── Summary schemas ──────────────────────────────────────────────────────────

class MonthOverMonth(BaseModel):
    current_month: Decimal
    previous_month: Decimal
    change_percent: Union[float, None]  # None if no previous month data


class CategoryInsight(BaseModel):
    category: str
    current_month: Decimal
    previous_month: Decimal
    change_percent: float
    flagged: bool  # True when change > 20%


class SummaryResponse(BaseModel):
    total_spend: Decimal
    by_category: dict[str, Decimal]
    month_over_month: MonthOverMonth
    insights: list[CategoryInsight]


# ── Auth schemas ──────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_must_not_be_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("username must not be blank")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("password must be at least 6 characters")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    is_active: bool

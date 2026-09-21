from sqlalchemy import Column, Integer, Numeric, String, Text, Date, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    note = Column(Text, nullable=True)
    date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

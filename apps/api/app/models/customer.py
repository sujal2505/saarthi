"""
Saarthi Finance — Customer ORM Model.
"""

from __future__ import annotations

from sqlalchemy import String, Integer, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Customer(Base):
    """Customer profile with demographics, income, and financial context."""

    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str | None] = mapped_column(String(300), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(5), default="en")
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(200), nullable=True)
    dependents: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Income & obligations
    monthly_income: Mapped[float] = mapped_column(Float, default=0.0)
    income_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    income_stability: Mapped[str] = mapped_column(
        String(20), default="stable"
    )  # stable / variable / declining

    # Existing obligations
    existing_emi: Mapped[float] = mapped_column(Float, default=0.0)
    total_debt: Mapped[float] = mapped_column(Float, default=0.0)
    credit_score_band: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Emergency savings
    emergency_fund: Mapped[float] = mapped_column(Float, default=0.0)

    # Risk / health summary (cached; recomputed by services)
    financial_health_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Password hash — demo only (never stored in plain text)
    password_hash: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Relationships
    transactions = relationship("Transaction", back_populates="customer", lazy="dynamic")
    goals = relationship("Goal", back_populates="customer", lazy="selectin")
    alerts = relationship("Alert", back_populates="customer", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Customer {self.id}: {self.name}>"

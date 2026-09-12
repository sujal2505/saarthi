"""
Saarthi Finance — Transaction ORM Model.
"""

from __future__ import annotations

from sqlalchemy import String, Integer, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime

from app.database import Base


class Transaction(Base):
    """Financial transaction record."""

    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    customer_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("customers.id"), nullable=False, index=True
    )
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False, index=True)
    merchant: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)  # credit / debit
    channel: Mapped[str | None] = mapped_column(String(50), nullable=True)
    recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationship
    customer = relationship("Customer", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction {self.id}: {self.merchant} ₹{self.amount}>"

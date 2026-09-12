"""
Saarthi Finance — Goal ORM Model.
"""

from __future__ import annotations

from sqlalchemy import String, Float, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime

from app.database import Base


class Goal(Base):
    """Financial goal (e.g., emergency fund, education savings)."""

    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    customer_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("customers.id"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    target_amount: Mapped[float] = mapped_column(Float, nullable=False)
    current_amount: Mapped[float] = mapped_column(Float, default=0.0)
    target_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    monthly_contribution: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationship
    customer = relationship("Customer", back_populates="goals")

    @property
    def progress_pct(self) -> float:
        if self.target_amount <= 0:
            return 100.0
        return round((self.current_amount / self.target_amount) * 100, 1)

    @property
    def months_remaining(self) -> int:
        if self.monthly_contribution <= 0:
            return 0
        remaining = self.target_amount - self.current_amount
        if remaining <= 0:
            return 0
        return max(1, int(remaining / self.monthly_contribution + 0.5))

    @property
    def on_track(self) -> bool:
        today = datetime.date.today()
        if self.target_date <= today:
            return self.current_amount >= self.target_amount
        months_left = max(1, (self.target_date.year - today.year) * 12 + (self.target_date.month - today.month))
        required_monthly = (self.target_amount - self.current_amount) / months_left
        return self.monthly_contribution >= required_monthly * 0.9  # 10% tolerance

    def __repr__(self) -> str:
        return f"<Goal {self.id}: {self.name} ({self.progress_pct}%)>"

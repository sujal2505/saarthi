"""
Saarthi Finance — Test Configuration and Fixtures.
"""

import datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.models.goal import Goal
from app.models.alert import Alert

# In-memory SQLite for fast, isolated tests
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test function."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Seed sample customer
    cust = Customer(
        id="cust_001",
        name="Ananya Verma",
        city="Indore",
        state="Madhya Pradesh",
        preferred_language="hi",
        phone="98XXXXX321",
        age=31,
        occupation="Marketing Executive",
        dependents=2,
        monthly_income=58000.0,
        income_source="Salary",
        income_stability="stable",
        existing_emi=9500.0,
        total_debt=180000.0,
        credit_score_band="Good",
        emergency_fund=60000.0,
        financial_health_score=76.0,
        risk_level="stable",
        password_hash="$2b$12$demo_hash",
    )
    session.add(cust)

    # Seed sample transactions
    txns = [
        Transaction(
            id="t1",
            customer_id="cust_001",
            date=datetime.date(2024, 9, 1),
            merchant="HDFC Salary Credit",
            category="Salary",
            amount=58000.0,
            type="credit",
            channel="NEFT",
            recurring=True,
            description="Monthly salary",
        ),
        Transaction(
            id="t2",
            customer_id="cust_001",
            date=datetime.date(2024, 9, 3),
            merchant="Indore Rent",
            category="Rent",
            amount=11000.0,
            type="debit",
            channel="NEFT",
            recurring=True,
            description="Rent",
        ),
        Transaction(
            id="t3",
            customer_id="cust_001",
            date=datetime.date(2024, 9, 10),
            merchant="SBI EMI",
            category="EMI",
            amount=9500.0,
            type="debit",
            channel="Auto-debit",
            recurring=True,
            description="Home loan EMI",
        ),
        Transaction(
            id="t4",
            customer_id="cust_001",
            date=datetime.date(2024, 9, 12),
            merchant="Reliance Fresh",
            category="Groceries",
            amount=3500.0,
            type="debit",
            channel="UPI",
            recurring=False,
            description="Groceries",
        ),
    ]
    session.add_all(txns)

    # Seed sample goal
    goal = Goal(
        id="g001",
        customer_id="cust_001",
        type="emergency_fund",
        name="Emergency Fund",
        target_amount=150000.0,
        current_amount=60000.0,
        target_date=datetime.date(2025, 6, 30),
        monthly_contribution=5000.0,
    )
    session.add(goal)

    # Seed sample alert
    alert = Alert(
        id="alert_001",
        customer_id="cust_001",
        type="cash_flow",
        severity="medium",
        title="Monthly expenses rising",
        description="Spending increased recently.",
        evidence="Aug vs Sep expenses",
        action="Review spending",
        action_label="Review",
    )
    session.add(alert)
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """FastAPI TestClient with overridden database session."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

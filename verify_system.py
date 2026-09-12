"""
Saarthi Finance — Quick System Verification Script

Runs pre-flight integration checks across all components:
1. Environment and package availability
2. Database and demo customer seeding
3. ML processed fixtures
4. FastAPI test client and live responses
5. Static frontend distribution
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding if needed
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent
API_DIR = ROOT_DIR / "apps" / "api"
sys.path.insert(0, str(API_DIR))


def check(name: str, fn):
    try:
        fn()
        print(f"  [PASS] {name}")
        return True
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        return False


def main():
    print("\n========================================")
    print("   Saarthi Finance -- System Verification")
    print("========================================\n")

    results = []

    # 1. Imports
    def test_imports():
        import fastapi
        import pydantic
        import sqlalchemy
        import uvicorn
    results.append(check("Core backend dependencies installed", test_imports))

    # 2. Database & Models
    def test_database():
        from app.database import SessionLocal, engine, Base
        from app.models.customer import Customer
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        count = db.query(Customer).count()
        db.close()
        assert count > 0, "No customer records found"
    results.append(check("Database initialized and seeded", test_database))

    # 3. ML Fixtures
    def test_ml_fixtures():
        dashboards_file = ROOT_DIR / "data" / "processed" / "dashboards.json"
        features_file = ROOT_DIR / "data" / "processed" / "customer_features.json"
        assert dashboards_file.is_file(), f"Missing {dashboards_file}"
        assert features_file.is_file(), f"Missing {features_file}"
    results.append(check("ML processed fixtures present", test_ml_fixtures))

    # 4. API & Endpoints
    def test_endpoints():
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)

        # Health
        res = client.get("/health")
        assert res.status_code == 200, f"Health check failed: {res.status_code}"

        # Customer
        res = client.get("/api/v1/customers/cust_001")
        assert res.status_code == 200, f"Customer fetch failed: {res.status_code}"
        assert res.json()["name"] == "Ananya Verma"

        # Dashboard
        res = client.get("/api/v1/customers/cust_001/dashboard")
        assert res.status_code == 200, f"Dashboard fetch failed: {res.status_code}"

        # Simulator
        res = client.post("/api/v1/simulator/emi", json={
            "loan_amount": 25000,
            "interest_rate": 12.0,
            "tenure_months": 12,
            "monthly_income": 45000,
            "existing_emi": 5000,
            "monthly_expenses": 20000
        })
        assert res.status_code == 200, f"Simulator failed: {res.status_code}"

        # Assistant
        res = client.post("/api/v1/assistant/chat", json={
            "customer_id": "cust_001",
            "message": "Hello, how is my financial health?",
            "language": "en"
        })
        assert res.status_code == 200, f"Assistant chat failed: {res.status_code}"
    results.append(check("FastAPI routes & ML models operating cleanly", test_endpoints))

    # 5. Frontend Static Distribution
    def test_frontend():
        dist_html = ROOT_DIR / "apps" / "web" / "dist" / "index.html"
        assert dist_html.is_file(), "Frontend dist/index.html missing"
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        res = client.get("/", headers={"accept": "text/html"})
        assert res.status_code == 200, "Frontend serving failed"
    results.append(check("Frontend web dist compiled & served via FastAPI", test_frontend))

    print()
    passed = sum(results)
    total = len(results)
    if passed == total:
        print(f"[SUCCESS] All {total} integration checks passed successfully!\n")
        print("To start the live platform:")
        print("  cd apps/api && python -m uvicorn app.main:app --reload --port 8000\n")
        print("Then open in browser:")
        print("  http://localhost:8000 (Full UI) or http://localhost:8000/docs (Swagger API Docs)\n")
    else:
        print(f"[FAIL] {total - passed} check(s) failed.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Integration tests for FastAPI endpoints.
"""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "disclaimer" in data


def test_auth_demo_login(client: TestClient):
    response = client.post("/api/v1/auth/demo-login", json={"phone": "98XXXXX321"})
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["customer_id"] == "cust_001"


def test_customer_profile(client: TestClient):
    response = client.get("/api/v1/customers/cust_001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "cust_001"
    assert data["name"] == "Ananya Verma"
    assert data["city"] == "Indore"


def test_customer_not_found(client: TestClient):
    response = client.get("/api/v1/customers/cust_nonexistent")
    assert response.status_code == 404


def test_dashboard_endpoint(client: TestClient):
    response = client.get("/api/v1/customers/cust_001/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "customer" in data
    assert "financial_health" in data
    assert "cash_flow" in data
    assert "recommendation" in data
    assert "recent_transactions" in data
    assert "goals" in data
    assert "monthly_trend" in data
    assert "spending_categories" in data


def test_transactions_endpoint(client: TestClient):
    response = client.get("/api/v1/customers/cust_001/transactions")
    assert response.status_code == 200
    txns = response.json()
    assert isinstance(txns, list)
    assert len(txns) > 0


def test_spending_endpoint(client: TestClient):
    response = client.get("/api/v1/customers/cust_001/spending")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_recommendations_endpoint(client: TestClient):
    response = client.get("/api/v1/customers/cust_001/recommendations")
    assert response.status_code == 200
    data = response.json()
    assert "type" in data
    assert "warning" in data


def test_alerts_endpoint(client: TestClient):
    response = client.get("/api/v1/customers/cust_001/alerts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_goals_list_and_create(client: TestClient):
    # 1. List goals
    response = client.get("/api/v1/customers/cust_001/goals")
    assert response.status_code == 200
    initial_goals = response.json()
    initial_count = len(initial_goals)

    # 2. Create new goal
    new_goal_payload = {
        "type": "festival",
        "name": "Holi Savings",
        "target_amount": 15000.0,
        "target_date": "2025-03-25",
        "monthly_contribution": 2500.0,
    }
    create_res = client.post("/api/v1/customers/cust_001/goals", json=new_goal_payload)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["name"] == "Holi Savings"
    assert created["target_amount"] == 15000.0

    # 3. Verify count incremented
    list_res = client.get("/api/v1/customers/cust_001/goals")
    assert len(list_res.json()) == initial_count + 1


def test_simulator_emi(client: TestClient):
    payload = {
        "loan_amount": 200000.0,
        "interest_rate": 10.5,
        "tenure_months": 24,
    }
    response = client.post("/api/v1/simulator/emi", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["monthly_emi"] > 0
    assert data["total_repayment"] > payload["loan_amount"]


def test_simulator_goal(client: TestClient):
    payload = {
        "target_amount": 100000.0,
        "current_savings": 20000.0,
        "monthly_contribution": 5000.0,
        "expected_return_rate": 6.0,
    }
    response = client.post("/api/v1/simulator/goal", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["months_to_goal"] > 0
    assert data["is_achievable"] is True


def test_assistant_chat(client: TestClient):
    payload = {
        "customer_id": "cust_001",
        "message": "Can you explain my savings rate and budget?",
        "language": "en",
    }
    response = client.post("/api/v1/assistant/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "disclaimer" in data


def test_transaction_csv_ingest(client: TestClient):
    csv_content = (
        "date,merchant,category,amount,type,channel,description\n"
        "2024-09-28,Local Dairy,Groceries,320,debit,UPI,Milk and butter\n"
    )
    files = {"file": ("test_txns.csv", csv_content.encode("utf-8"), "text/csv")}
    data = {"customer_id": "cust_001"}
    response = client.post("/api/v1/transactions/ingest", data=data, files=files)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["inserted"] == 1

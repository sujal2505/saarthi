# Saarthi Finance — Integration & Troubleshooting Log

> Detailed log of integration touchpoints across frontend, backend, database, and ML layers, along with documented resolutions and fallback mechanisms.

---

## 1. Resolved Integration Issues

### Issue 1: Customer Profile Endpoint `NameError`
- **Location:** `apps/api/app/routers/customer.py` (`GET /api/v1/customers/{customer_id}`)
- **Symptom:** Endpoint raised `NameError: name 'customer' is not defined` when resolving customer profile, failing integration tests.
- **Root Cause:** The handler returned `CustomerResponse.model_validate(customer)` without querying the database session for `Customer`.
- **Resolution:** Added `db.query(Customer).filter(Customer.id == customer_id).first()` with a proper 404 `HTTPException` if not found.
- **Status:** **RESOLVED** (27/27 pytest tests passing).

### Issue 2: Relative SQLite Database Path Resolution
- **Location:** `apps/api/app/config.py` (`database_url`)
- **Symptom:** When running commands or tests from the root workspace directory, `./saarthi.db` created an unseeded SQLite file at repo root rather than accessing `apps/api/saarthi.db`.
- **Root Cause:** Default `database_url` was `"sqlite:///./saarthi.db"` (relative to working directory).
- **Resolution:** Configured `_DEFAULT_DB_FILE = _API_DIR / "saarthi.db"` with an absolute path anchor, ensuring consistent database connection regardless of execution CWD.
- **Status:** **RESOLVED**.

### Issue 3: Unified Single-Port Demonstration
- **Location:** `apps/api/app/main.py`
- **Challenge:** Running separate frontend (Vite port 5173) and backend (FastAPI port 8000) servers requires dual terminals and process management during live hackathon demos.
- **Resolution:** Mounted `apps/web/dist` directly inside FastAPI via `StaticFiles` and `FileResponse`. Browsing `http://localhost:8000` or `http://localhost:8000/app` immediately delivers the full React SPA, while `/api/v1/*` and `/docs` serve the API and Swagger UI.
- **Status:** **RESOLVED**.

---

## 2. Pre-Flight Verification

To verify that all system components (dependencies, database, ML fixtures, API endpoints, and frontend bundle) are operating properly, run:

```powershell
& "apps/api/.venv/Scripts/python.exe" verify_system.py
```

All 5 core checks should pass:
1. `Core backend dependencies installed`
2. `Database initialized and seeded`
3. `ML processed fixtures present`
4. `FastAPI routes & ML models operating cleanly`
5. `Frontend web dist compiled & served via FastAPI`

---

## 3. How to Run the Platform

### Option A: Unified Server (Recommended for Demos)
Run the FastAPI application which serves both backend APIs and the built frontend:

```powershell
cd apps/api
& ".venv/Scripts/python.exe" -m uvicorn app.main:app --reload --port 8000
```
- Open UI: **http://localhost:8000**
- Open API Docs: **http://localhost:8000/docs**

### Option B: Independent Vite Dev Server
If modifying React source code with HMR:

```powershell
cd apps/web
npm run dev
```
- Open Vite UI: **http://localhost:5173** (automatically proxies to backend at `http://localhost:8000`)

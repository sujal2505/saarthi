"""
Saarthi Finance — FastAPI Application Entry Point.

Core Principle:
Responsible financial guidance platform for Bharat.
Decision-support only — never claims to automatically approve or reject loans.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from sqlalchemy import inspect, text

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.seed import seed_database
from app.routers import (
    health,
    auth,
    customer,
    dashboard,
    transactions,
    spending,
    recommendations,
    alerts,
    goals,
    simulator,
    assistant,
    ingest,
)

# Logging configuration
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("saarthi-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown events.
    Creates tables and seeds synthetic demo data on first start.
    """
    logger.info("Initializing Saarthi Finance database...")
    Base.metadata.create_all(bind=engine)
    if "address" not in {column["name"] for column in inspect(engine).get_columns("customers")}:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE customers ADD COLUMN address VARCHAR(300)"))

    # Seed demo data if database is empty
    db = SessionLocal()
    try:
        seed_database(db, force=False)
        logger.info("Database initialized and demo data verified.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
    finally:
        db.close()

    yield

    logger.info("Saarthi Finance API shutting down.")


app = FastAPI(
    title="Saarthi Finance API",
    description=(
        "AI-Powered Hyper-Personalized Banking Platform for Bharat.\n\n"
        "**Core Principle & Governance Notice:**\n"
        "Saarthi Finance is a responsible advisory decision-support platform. "
        "It provides explainable financial guidance and simulations. "
        "It **never** automatically approves or rejects loans or financial products. "
        "All recommendations require qualified human review and customer consent."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration — allow localhost and 127.0.0.1 on any port for frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error processing {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please consult platform logs.",
            "path": request.url.path,
        },
    )


# Register Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(customer.router)
app.include_router(dashboard.router)
app.include_router(transactions.router)
app.include_router(spending.router)
app.include_router(recommendations.router)
app.include_router(alerts.router)
app.include_router(goals.router)
app.include_router(simulator.router)
app.include_router(assistant.router)
app.include_router(ingest.router)


from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

# Check for compiled frontend distribution
WEB_DIST_DIR = Path(__file__).resolve().parent.parent.parent / "web" / "dist"
if (WEB_DIST_DIR / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=str(WEB_DIST_DIR / "assets")), name="static_assets")


@app.get("/favicon.svg", include_in_schema=False)
async def serve_favicon():
    if (WEB_DIST_DIR / "favicon.svg").is_file():
        return FileResponse(WEB_DIST_DIR / "favicon.svg")
    return JSONResponse(status_code=404, content={"detail": "Not found"})


@app.get("/icons.svg", include_in_schema=False)
async def serve_icons():
    if (WEB_DIST_DIR / "icons.svg").is_file():
        return FileResponse(WEB_DIST_DIR / "icons.svg")
    return JSONResponse(status_code=404, content={"detail": "Not found"})


@app.get("/", tags=["Root"])
async def root(request: Request):
    if "text/html" in request.headers.get("accept", "") and (WEB_DIST_DIR / "index.html").is_file():
        return FileResponse(WEB_DIST_DIR / "index.html")
    return {
        "platform": "Saarthi Finance",
        "description": "AI-powered hyper-personalized banking for Bharat",
        "status": "active",
        "docs": "/docs",
        "app": "/app",
        "disclaimer": (
            "Decision support only. Saarthi Finance never claims to approve or "
            "reject loans automatically."
        ),
    }


@app.get("/app", include_in_schema=False)
@app.get("/app/{full_path:path}", include_in_schema=False)
async def serve_app(full_path: str = ""):
    if (WEB_DIST_DIR / "index.html").is_file():
        return FileResponse(WEB_DIST_DIR / "index.html")
    return JSONResponse(status_code=404, content={"detail": "Frontend build not found"})


@app.api_route("/api/v1/seed/reload", methods=["GET", "POST"], tags=["Seed Data"])
async def reload_seed():
    """Reload all customer profiles, goals, alerts, and transactions from transactions.csv."""
    db = SessionLocal()
    try:
        seed_database(db, force=True)
        return {
            "status": "success",
            "message": "Database successfully reloaded from data/seed/transactions.csv",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


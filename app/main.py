from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import expenses, summary, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup (Expense + User)
    Base.metadata.create_all(bind=engine)
    from app.database import SessionLocal
    from app.services import auth_service
    db = SessionLocal()
    try:
        for demo_name in ["demo@example.com", "demo"]:
            if not auth_service.get_user_by_username(db, demo_name):
                auth_service.create_user(db, demo_name, "password123")
    except Exception:
        pass
    finally:
        db.close()
    yield


app = FastAPI(
    title="Spend Tracker API",
    description="A simple expense tracking REST API built with FastAPI + SQLite.",
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)        # /auth/register, /auth/login, /auth/me
app.include_router(expenses.router)    # /expenses  (JWT protected)
app.include_router(summary.router)     # /summary   (JWT protected)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "message": "Spend Tracker API is running"}

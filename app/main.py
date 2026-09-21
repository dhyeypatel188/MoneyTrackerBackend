from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.database import engine, Base
from app.routers import expenses, summary, auth
from app.common.response import build_response


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


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    envelope = build_response(
        status_code=exc.status_code,
        status_desc=str(exc.detail) if isinstance(exc.detail, str) else "Error",
        error_details=exc.detail if not isinstance(exc.detail, str) else None,
        path=str(request.url.path),
        method=request.method,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=envelope,
        headers=getattr(exc, "headers", None),
    )


from fastapi.encoders import jsonable_encoder


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = jsonable_encoder(exc.errors())
    status_desc = errors[0]["msg"] if errors and "msg" in errors[0] else "Validation error"
    envelope = build_response(
        status_code=422,
        status_desc=status_desc,
        error_type="Unprocessable Entity",
        error_details=errors,
        path=str(request.url.path),
        method=request.method,
    )
    return JSONResponse(status_code=422, content=envelope)


# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://trackspendings.netlify.app",
    ],
    allow_origin_regex=r"https://.*\.netlify\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)        # /auth/register, /auth/login, /auth/me, /auth/logout
app.include_router(expenses.router)    # /expenses  (JWT protected)
app.include_router(summary.router)     # /summary   (JWT protected)


@app.get("/", tags=["health"])
def root(request: Request):
    return build_response(
        status_code=200,
        status_desc="Spend Tracker API is running",
        data={"status": "ok", "message": "Spend Tracker API is running"},
        path=str(request.url.path),
        method=request.method,
    )

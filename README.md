# Spend Tracker — Backend API

A REST API built with **FastAPI** + **SQLAlchemy** + **SQLite** with JWT authentication and bcrypt password hashing for tracking personal expenses.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+

### 2. Create Virtual Environment & Install Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt)
venv\Scripts\activate.bat

# macOS / Linux
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Default settings in `.env`:
```ini
DATABASE_URL=sqlite:///./expenses.db
JWT_SECRET=super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

- API Base URL: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc UI: `http://localhost:8000/redoc`

> 💡 Default demo user (`demo@example.com` / `password123`) is automatically seeded on startup.

---

## 📡 API Endpoints

Protected endpoints require the header:
`Authorization: Bearer <access_token>`

### Authentication Routes

| Method | Endpoint | Description | Auth Required |
|---|---|---|:---:|
| `POST` | `/auth/register` | Register new user | No |
| `POST` | `/auth/login` | Login with username & password | No |
| `POST` | `/auth/logout` | Sign out / invalidate session | Optional / Bearer |
| `GET` | `/auth/me` | Fetch authenticated user profile | Bearer Token |

### Expense Routes

| Method | Endpoint | Description | Auth Required |
|---|---|---|:---:|
| `POST` | `/expenses` | Create a new expense | Bearer Token |
| `GET` | `/expenses` | List expenses (supports query params: `category`, `from_date`, `to_date`) | Bearer Token |

### Summary & Analytics Route

| Method | Endpoint | Description | Auth Required |
|---|---|---|:---:|
| `GET` | `/summary` | Aggregated spend totals, category breakdown, MoM change, and >20% spike warnings | Bearer Token |

---

## 🧪 Running Tests

```bash
# From backend/ with venv activated
pytest -v
```

---

## 🏗️ Project Structure & Architecture

A modular 3-layer architecture was set up to maintain separation of concerns and clear folder boundaries:

```text
backend/
├── app/
│   ├── routers/       # HTTP request handlers & routing (/auth, /expenses, /summary)
│   ├── services/      # Business logic (JWT/bcrypt auth, MoM calculations, spike detection)
│   ├── dependencies.py# Reusable FastAPI dependencies (JWT Bearer authentication)
│   ├── models.py      # SQLAlchemy ORM database models (User, Expense)
│   ├── schemas.py     # Pydantic v2 validation contracts & response shapes
│   ├── database.py    # Database connection & session management
│   ├── config.py      # Environment configuration via pydantic-settings
│   └── main.py        # App initialization, CORS, and automatic DB/user seeding
├── tests/             # Pytest test suite with isolated test DB fixtures
├── expenses.db        # SQLite database
├── requirements.txt   # Pinned dependencies
├── .env.example       # Safe template for environment variables
└── .gitignore         # Ignored credentials, virtual environments, and caches
```

---

AI Usage Note

I utilized **Antigravity** (Google DeepMind) as an AI pair-programmer to scaffold initial boilerplate, route definitions, and test fixtures. I actively guided and structured the modular folder hierarchy (`routers/` vs `services/` vs `models/`)
It did not call the sighout API so i add that 
Test everthing before submitting
Fix the API response structure

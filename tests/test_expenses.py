"""
Tests for POST /expenses and GET /expenses — happy path + edge cases.
"""
from tests.conftest import API_KEY_HEADERS


def test_create_expense_success(client):
    """Happy path: valid expense is created and returned."""
    resp = client.post(
        "/expenses",
        json={"amount": "49.99", "category": "Food", "note": "Lunch", "date": "2026-09-01"},
        headers=API_KEY_HEADERS,
    )
    assert resp.status_code == 201
    data = resp.json()["responseObject"]["data"]
    assert data["amount"] == "49.99"
    assert data["category"] == "Food"
    assert data["note"] == "Lunch"
    assert data["date"] == "2026-09-01"
    assert "id" in data


def test_create_expense_defaults_to_today(client):
    """Date should default to today when not provided."""
    from datetime import date
    resp = client.post(
        "/expenses",
        json={"amount": "10.00", "category": "Transport"},
        headers=API_KEY_HEADERS,
    )
    assert resp.status_code == 201
    assert resp.json()["responseObject"]["data"]["date"] == date.today().isoformat()


def test_create_expense_negative_amount(client):
    """Negative amount must be rejected with 422."""
    resp = client.post(
        "/expenses",
        json={"amount": "-5.00", "category": "Food"},
        headers=API_KEY_HEADERS,
    )
    assert resp.status_code == 422
    assert "amount" in resp.text.lower()


def test_create_expense_zero_amount(client):
    """Zero amount must be rejected with 422."""
    resp = client.post(
        "/expenses",
        json={"amount": "0", "category": "Food"},
        headers=API_KEY_HEADERS,
    )
    assert resp.status_code == 422


def test_create_expense_missing_category(client):
    """Missing category must be rejected with 422."""
    resp = client.post(
        "/expenses",
        json={"amount": "20.00"},
        headers=API_KEY_HEADERS,
    )
    assert resp.status_code == 422


def test_create_expense_blank_category(client):
    """Blank/whitespace-only category must be rejected."""
    resp = client.post(
        "/expenses",
        json={"amount": "20.00", "category": "   "},
        headers=API_KEY_HEADERS,
    )
    assert resp.status_code == 422


def test_create_expense_missing_amount(client):
    """Missing amount must be rejected with 422."""
    resp = client.post(
        "/expenses",
        json={"category": "Food"},
        headers=API_KEY_HEADERS,
    )
    assert resp.status_code == 422


def test_create_expense_invalid_date(client):
    """Invalid date format must be rejected."""
    resp = client.post(
        "/expenses",
        json={"amount": "10.00", "category": "Food", "date": "not-a-date"},
        headers=API_KEY_HEADERS,
    )
    assert resp.status_code == 422


def test_list_expenses_empty(client):
    """GET /expenses on empty DB returns empty list."""
    resp = client.get("/expenses", headers=API_KEY_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["responseObject"]["data"] == []


def test_list_expenses_returns_all(client):
    """All created expenses are returned."""
    for cat in ["Food", "Travel", "Food"]:
        client.post("/expenses", json={"amount": "10.00", "category": cat}, headers=API_KEY_HEADERS)
    resp = client.get("/expenses", headers=API_KEY_HEADERS)
    assert resp.status_code == 200
    assert len(resp.json()["responseObject"]["data"]) == 3


def test_list_expenses_filter_by_category(client):
    """Filter by category returns only matching expenses (case-insensitive)."""
    client.post("/expenses", json={"amount": "10.00", "category": "Food"}, headers=API_KEY_HEADERS)
    client.post("/expenses", json={"amount": "20.00", "category": "Travel"}, headers=API_KEY_HEADERS)

    resp = client.get("/expenses?category=food", headers=API_KEY_HEADERS)
    assert resp.status_code == 200
    results = resp.json()["responseObject"]["data"]
    assert len(results) == 1
    assert results[0]["category"] == "Food"


def test_list_expenses_filter_by_date_range(client):
    """Filter by date range returns only expenses within the range."""
    client.post("/expenses", json={"amount": "10.00", "category": "Food", "date": "2026-08-01"}, headers=API_KEY_HEADERS)
    client.post("/expenses", json={"amount": "20.00", "category": "Food", "date": "2026-09-15"}, headers=API_KEY_HEADERS)
    client.post("/expenses", json={"amount": "30.00", "category": "Food", "date": "2026-10-01"}, headers=API_KEY_HEADERS)

    resp = client.get("/expenses?from_date=2026-09-01&to_date=2026-09-30", headers=API_KEY_HEADERS)
    assert resp.status_code == 200
    results = resp.json()["responseObject"]["data"]
    assert len(results) == 1
    assert results[0]["amount"] == "20.00"


def test_list_expenses_invalid_date_range(client):
    """from_date > to_date must return 400."""
    resp = client.get("/expenses?from_date=2026-10-01&to_date=2026-09-01", headers=API_KEY_HEADERS)
    assert resp.status_code == 400


def test_missing_api_key_rejected(client):
    """Requests without auth must be rejected with 401."""
    from app.main import app
    from app.dependencies import get_current_user
    saved = app.dependency_overrides.pop(get_current_user, None)
    try:
        resp = client.get("/expenses")
        assert resp.status_code in (401, 403)
    finally:
        if saved:
            app.dependency_overrides[get_current_user] = saved


def test_wrong_api_key_rejected(client):
    """Requests with wrong auth must be rejected with 401."""
    from app.main import app
    from app.dependencies import get_current_user
    saved = app.dependency_overrides.pop(get_current_user, None)
    try:
        resp = client.get("/expenses", headers={"Authorization": "Bearer invalid-token"})
        assert resp.status_code in (401, 403)
    finally:
        if saved:
            app.dependency_overrides[get_current_user] = saved

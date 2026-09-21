"""
Tests for GET /summary — totals, MoM, and the 20% spike insight.
"""
from tests.conftest import API_KEY_HEADERS


def _add(client, amount, category, date):
    client.post(
        "/expenses",
        json={"amount": str(amount), "category": category, "date": date},
        headers=API_KEY_HEADERS,
    )


def test_summary_empty_db(client):
    """Summary on empty DB returns all zeros and no insights."""
    resp = client.get("/summary", headers=API_KEY_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert float(data["total_spend"]) == 0.0
    assert data["by_category"] == {}
    assert data["insights"] == []
    assert float(data["month_over_month"]["current_month"]) == 0.0
    assert float(data["month_over_month"]["previous_month"]) == 0.0
    assert data["month_over_month"]["change_percent"] is None


def test_summary_total_spend(client):
    """Total spend aggregates all expenses correctly."""
    _add(client, 100, "Food", "2026-09-01")
    _add(client, 200, "Travel", "2026-09-05")
    _add(client, 50, "Food", "2026-09-10")

    resp = client.get("/summary", headers=API_KEY_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert float(data["total_spend"]) == 350.0
    assert float(data["by_category"]["Food"]) == 150.0
    assert float(data["by_category"]["Travel"]) == 200.0


def test_summary_mom_no_previous_month(client):
    """MoM change_percent is None when no previous-month data exists."""
    from datetime import date
    today = date.today().isoformat()
    _add(client, 500, "Food", today)

    resp = client.get("/summary", headers=API_KEY_HEADERS)
    data = resp.json()
    assert data["month_over_month"]["change_percent"] is None


def test_summary_mom_increase(client):
    """MoM correctly calculates positive percentage change."""
    # Previous month
    _add(client, 400, "Food", "2026-08-15")
    # Current month
    _add(client, 500, "Food", "2026-09-15")

    resp = client.get("/summary", headers=API_KEY_HEADERS)
    mom = resp.json()["month_over_month"]
    # 500-400=100, 100/400 * 100 = 25%
    assert abs(mom["change_percent"] - 25.0) < 0.1


def test_summary_mom_decrease(client):
    """MoM correctly calculates negative percentage change."""
    _add(client, 600, "Food", "2026-08-15")
    _add(client, 300, "Food", "2026-09-15")

    resp = client.get("/summary", headers=API_KEY_HEADERS)
    mom = resp.json()["month_over_month"]
    # (300-600)/600 * 100 = -50%
    assert abs(mom["change_percent"] - (-50.0)) < 0.1


def test_summary_insight_flagged_above_20_percent(client):
    """Category with >20% MoM increase is flagged in insights."""
    _add(client, 100, "Food", "2026-08-15")
    _add(client, 130, "Food", "2026-09-15")  # +30%

    resp = client.get("/summary", headers=API_KEY_HEADERS)
    insights = resp.json()["insights"]
    food_insight = next((i for i in insights if i["category"] == "Food"), None)

    assert food_insight is not None
    assert food_insight["flagged"] is True
    assert food_insight["change_percent"] > 20


def test_summary_insight_not_flagged_below_20_percent(client):
    """Category with <=20% MoM increase is NOT flagged."""
    _add(client, 100, "Food", "2026-08-15")
    _add(client, 115, "Food", "2026-09-15")  # +15%

    resp = client.get("/summary", headers=API_KEY_HEADERS)
    insights = resp.json()["insights"]
    food_insight = next((i for i in insights if i["category"] == "Food"), None)

    assert food_insight is not None
    assert food_insight["flagged"] is False


def test_summary_new_category_flagged(client):
    """Brand-new category (not in previous month) is flagged as 100% increase."""
    _add(client, 200, "Travel", "2026-09-15")

    resp = client.get("/summary", headers=API_KEY_HEADERS)
    insights = resp.json()["insights"]
    travel = next((i for i in insights if i["category"] == "Travel"), None)

    assert travel is not None
    assert travel["flagged"] is True
    assert travel["change_percent"] == 100.0

import os

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

TEST_API_KEY = os.getenv("SIGNAL_API_KEY", "test-key")


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_no_auth_required():
    # Health must work without API key
    response = client.get("/health")
    assert response.status_code == 200


def test_invalid_ticker_returns_404():
    response = client.get(
        "/api/company/INVALID",
        headers={"X-Signal-Key": TEST_API_KEY},
    )
    assert response.status_code == 404
    assert "coverage universe" in response.json()["detail"].lower()


def test_missing_api_key_returns_401():
    response = client.get("/api/company/NVDA")
    assert response.status_code == 401


def test_chat_empty_question_returns_400():
    response = client.post(
        "/api/chat/query",
        headers={"X-Signal-Key": TEST_API_KEY},
        json={"question": "", "history": []},
    )
    assert response.status_code == 400


def test_chat_question_too_long_returns_400():
    response = client.post(
        "/api/chat/query",
        headers={"X-Signal-Key": TEST_API_KEY},
        json={"question": "x" * 2001, "history": []},
    )
    assert response.status_code == 400


def test_compare_too_many_tickers_returns_400():
    response = client.post(
        "/api/compare",
        headers={"X-Signal-Key": TEST_API_KEY},
        json={"tickers": ["NVDA", "AMD", "MSFT", "TSLA"]},
    )
    assert response.status_code == 400


def test_sectors_returns_list():
    response = client.get(
        "/api/sectors",
        headers={"X-Signal-Key": TEST_API_KEY},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

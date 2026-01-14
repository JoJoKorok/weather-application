import pytest
from fastapi.testclient import TestClient

import proxy.server as server
from proxy.server import app as proxy_app


class DummyHTTPXResponse:
    # Mimics httpx response for proxy tests.
    def __init__(self, status_code=200, data=None, text=""):
        self.status_code = status_code
        self._data = data or {}
        self.text = text

    def json(self):
        return self._data


class DummyAsyncClient:
    # Replaces httpx.AsyncClient so we never hit OpenWeather during tests.
    def __init__(self, timeout=8):
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, params=None):
        data = {
            "name": "London",
            "sys": {"country": "GB"},
            "main": {"temp": 1.0, "humidity": 90},
            "wind": {"speed": 1.5},
            "weather": [{"description": "few clouds"}],
        }
        return DummyHTTPXResponse(200, data=data)


def test_proxy_root_ok():
    # Basic sanity check: proxy is alive.
    client = TestClient(proxy_app)
    r = client.get("/")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_proxy_requires_city_or_postal(monkeypatch):
    # Ensures missing query params return 400 instead of crashing.

    monkeypatch.setattr(server, "OPENWEATHER_API_KEY", "dummykey", raising=False)
    monkeypatch.setattr(server, "PROXY_TOKENS", set(), raising=False)

    client = TestClient(proxy_app)
    r = client.get("/weather")
    assert r.status_code == 400


def test_proxy_unauthorized_when_tokens_enabled(monkeypatch):
    # Ensures token gating works when PROXY_TOKENS is set.

    monkeypatch.setattr(server, "OPENWEATHER_API_KEY", "dummykey", raising=False)
    monkeypatch.setattr(server, "PROXY_TOKENS", {"allowedtoken"}, raising=False)

    client = TestClient(proxy_app)
    r = client.get("/weather?city=London&country=gb")
    assert r.status_code == 401


def test_proxy_weather_success(monkeypatch):
    # Ensures proxy returns the fields the client expects.

    monkeypatch.setattr(server, "OPENWEATHER_API_KEY", "dummykey", raising=False)
    monkeypatch.setattr(server, "PROXY_TOKENS", set(), raising=False)

    # Avoid real network by swapping httpx.AsyncClient
    monkeypatch.setattr(server.httpx, "AsyncClient", DummyAsyncClient)

    client = TestClient(proxy_app)
    r = client.get("/weather?city=London&country=gb")

    assert r.status_code == 200
    body = r.json()

    assert "name" in body
    assert "main" in body
    assert "wind" in body
    assert "weather" in body

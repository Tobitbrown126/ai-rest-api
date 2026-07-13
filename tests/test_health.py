"""Tests for the public health/root/version endpoints."""


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "message" in body
    assert body["docs_url"] == "/docs"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"


def test_version(client):
    response = client.get("/version")
    assert response.status_code == 200
    body = response.json()
    assert "version" in body
    assert "app_name" in body

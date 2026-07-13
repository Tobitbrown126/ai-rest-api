"""Tests for authentication enforcement on protected routes."""


def test_chat_requires_auth(client):
    response = client.post("/chat", json={"message": "Hello"})
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False


def test_chat_with_valid_api_key(client, auth_headers):
    response = client.post("/chat", json={"message": "Hello"}, headers=auth_headers)
    assert response.status_code == 200


def test_chat_with_invalid_api_key(client):
    response = client.post(
        "/chat", json={"message": "Hello"}, headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == 401


def test_chat_with_invalid_bearer_token(client):
    response = client.post(
        "/chat",
        json={"message": "Hello"},
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert response.status_code == 401


def test_chat_with_valid_bearer_token(client):
    from auth import create_access_token

    token = create_access_token(subject="test-user")
    response = client.post(
        "/chat", json={"message": "Hello"}, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

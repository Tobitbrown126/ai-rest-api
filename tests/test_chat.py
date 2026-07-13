"""Tests for the /chat endpoint, including validation and conversation flow."""


def test_chat_basic(client, auth_headers):
    response = client.post("/chat", json={"message": "Hello there"}, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["reply"]
    assert body["conversation_id"]
    assert body["model"]


def test_chat_continues_conversation(client, auth_headers):
    first = client.post("/chat", json={"message": "Hi"}, headers=auth_headers).json()
    conversation_id = first["conversation_id"]

    second = client.post(
        "/chat",
        json={"message": "Follow up", "conversation_id": conversation_id},
        headers=auth_headers,
    )
    assert second.status_code == 200
    assert second.json()["conversation_id"] == conversation_id


def test_chat_unknown_conversation_id_returns_404(client, auth_headers):
    response = client.post(
        "/chat",
        json={"message": "Hi", "conversation_id": "does-not-exist"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_chat_rejects_empty_message(client, auth_headers):
    response = client.post("/chat", json={"message": "   "}, headers=auth_headers)
    assert response.status_code == 422


def test_chat_rejects_missing_message(client, auth_headers):
    response = client.post("/chat", json={}, headers=auth_headers)
    assert response.status_code == 422


def test_chat_rejects_invalid_temperature(client, auth_headers):
    response = client.post(
        "/chat", json={"message": "Hi", "temperature": 5.0}, headers=auth_headers
    )
    assert response.status_code == 422

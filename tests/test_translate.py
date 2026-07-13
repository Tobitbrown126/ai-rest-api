"""Tests for the /translate endpoint."""


def test_translate_success(client, auth_headers):
    response = client.post(
        "/translate",
        json={"text": "Hello, how are you?", "target_language": "Spanish"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["target_language"] == "Spanish"
    assert body["translated_text"]


def test_translate_requires_target_language(client, auth_headers):
    response = client.post("/translate", json={"text": "Hello"}, headers=auth_headers)
    assert response.status_code == 422


def test_translate_requires_auth(client):
    response = client.post(
        "/translate", json={"text": "Hello", "target_language": "French"}
    )
    assert response.status_code == 401

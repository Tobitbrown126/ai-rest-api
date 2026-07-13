"""Tests for the /summarize endpoint."""


def test_summarize_success(client, auth_headers):
    response = client.post(
        "/summarize",
        json={"text": "This is a long piece of text. " * 20, "length": "short"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["summary"]
    assert body["original_length_chars"] > 0


def test_summarize_rejects_empty_text(client, auth_headers):
    response = client.post("/summarize", json={"text": ""}, headers=auth_headers)
    assert response.status_code == 422


def test_summarize_invalid_length_enum(client, auth_headers):
    response = client.post(
        "/summarize", json={"text": "Some text", "length": "extra-long"}, headers=auth_headers
    )
    assert response.status_code == 422

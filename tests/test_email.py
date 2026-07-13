"""Tests for the /email endpoint."""


def test_generate_email_success(client, auth_headers):
    response = client.post(
        "/email",
        json={
            "subject_hint": "Project update",
            "key_points": ["We finished phase 1", "Phase 2 starts Monday"],
            "tone": "formal",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["subject"]
    assert body["body"]
    assert body["tone"] == "formal"


def test_generate_email_requires_key_points(client, auth_headers):
    response = client.post(
        "/email", json={"subject_hint": "Hello", "key_points": []}, headers=auth_headers
    )
    assert response.status_code == 422

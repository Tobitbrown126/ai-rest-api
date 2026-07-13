"""Tests for the /code/explain, /code/review, and /code/refactor endpoints."""

SAMPLE_CODE = "def add(a, b):\n    return a + b\n"


def test_code_explain(client, auth_headers):
    response = client.post(
        "/code/explain",
        json={"code": SAMPLE_CODE, "language": "python"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["explanation"]
    assert body["language"] == "python"


def test_code_review(client, auth_headers):
    response = client.post(
        "/code/review",
        json={"code": SAMPLE_CODE, "language": "python", "focus_areas": ["readability"]},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert "summary" in body
    assert isinstance(body["issues"], list)


def test_code_refactor(client, auth_headers):
    response = client.post(
        "/code/refactor",
        json={"code": SAMPLE_CODE, "language": "python", "goals": ["add type hints"]},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["refactored_code"]
    assert body["explanation_of_changes"]


def test_code_explain_rejects_empty_code(client, auth_headers):
    response = client.post(
        "/code/explain", json={"code": "", "language": "python"}, headers=auth_headers
    )
    assert response.status_code == 422


def test_code_endpoints_require_auth(client):
    response = client.post("/code/explain", json={"code": SAMPLE_CODE})
    assert response.status_code == 401

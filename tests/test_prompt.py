"""Tests for the /prompt/improve, /prompt/optimize, and /prompt/evaluate endpoints."""


def test_prompt_improve(client, auth_headers):
    response = client.post(
        "/prompt/improve",
        json={"prompt": "write about dogs", "goal": "produce a blog outline"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["improved_prompt"]
    assert body["rationale"]


def test_prompt_optimize(client, auth_headers):
    response = client.post(
        "/prompt/optimize",
        json={"prompt": "summarize this", "optimize_for": "brevity"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["optimized_prompt"]
    assert isinstance(body["changes_made"], list)


def test_prompt_evaluate(client, auth_headers):
    response = client.post(
        "/prompt/evaluate",
        json={"prompt": "Write me something good."},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert 1 <= body["scores"]["overall"] <= 10
    assert isinstance(body["strengths"], list)


def test_prompt_evaluate_rejects_empty_prompt(client, auth_headers):
    response = client.post("/prompt/evaluate", json={"prompt": ""}, headers=auth_headers)
    assert response.status_code == 422

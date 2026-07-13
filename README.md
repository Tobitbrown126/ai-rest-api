# ai-rest-api

A production-quality **AI REST API** built with **FastAPI**, exposing chat,
translation, summarization, email generation, code assistance, and prompt
engineering endpoints powered by the **OpenAI Responses API**.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Folder Structure](#folder-structure)
- [Installation Guide](#installation-guide)
  - [1. Install Python](#1-install-python)
  - [2. Visual Studio Code Setup](#2-visual-studio-code-setup)
  - [3. Create a Virtual Environment](#3-create-a-virtual-environment)
  - [4. Install Dependencies](#4-install-dependencies)
  - [5. Configure `.env`](#5-configure-env)
  - [6. Obtaining an OpenAI API Key](#6-obtaining-an-openai-api-key)
  - [7. Database Setup](#7-database-setup)
  - [8. Running Alembic Migrations](#8-running-alembic-migrations)
  - [9. Running the Server](#9-running-the-server)
- [API Authentication](#api-authentication)
- [API Endpoints](#api-endpoints)
- [Example Requests & Responses](#example-requests--responses)
- [cURL Examples](#curl-examples)
- [Postman Examples](#postman-examples)
- [Swagger & ReDoc Documentation](#swagger--redoc-documentation)
- [Testing](#testing)
- [Error Handling](#error-handling)
- [Troubleshooting](#troubleshooting)
- [Deployment Guide](#deployment-guide)
- [Docker](#docker-optional)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview

`ai-rest-api` is a reference implementation of a modern, secure, and
scalable REST API that wraps the OpenAI **Responses API** behind a set of
purpose-built endpoints: conversational chat with persisted history,
translation, summarization, email drafting, code explanation/review/
refactoring, and prompt engineering tools (improve/optimize/evaluate).

It is designed to demonstrate the practices expected in a production
backend service at a professional engineering organization: layered
architecture, dependency injection, structured logging, authentication,
rate limiting, database migrations, and a comprehensive automated test
suite.

## Features

- ✅ 12 REST endpoints covering chat, translation, summarization, email,
  code assistance, and prompt engineering
- ✅ OpenAI **Responses API** integration: system prompts, temperature
  control, structured/JSON output, streaming (SSE), function calling, and
  multi-turn conversation context
- ✅ Dual authentication: **API Key** (`X-API-Key`) and **JWT Bearer Token**
- ✅ SQLAlchemy ORM models with **SQLite** (default) and **PostgreSQL**
  support, plus **Alembic** migrations
- ✅ Conversation history persistence and API usage logging
- ✅ Structured logging via **Loguru** (console + rotating JSON file)
- ✅ Custom middleware: request/response logging, rate limiting, auth context
- ✅ Centralized exception handling with consistent JSON error envelopes
- ✅ Full **Pydantic v2** request/response validation
- ✅ Auto-generated **Swagger UI** and **ReDoc** documentation
- ✅ **Pytest** test suite covering endpoints, validation, auth, and errors
- ✅ Docker & docker-compose for containerized deployment

## Technology Stack

| Layer            | Technology                                  |
|-------------------|----------------------------------------------|
| Language          | Python 3.12+                                 |
| Web framework     | FastAPI                                      |
| ASGI server       | Uvicorn                                      |
| Validation        | Pydantic v2                                  |
| AI provider       | OpenAI Python SDK (Responses API)            |
| HTTP client       | HTTPX                                        |
| ORM               | SQLAlchemy 2.0                               |
| Migrations        | Alembic                                      |
| Database          | SQLite (default) / PostgreSQL                |
| Logging           | Loguru                                       |
| Testing           | Pytest, pytest-asyncio                       |
| Auth              | PyJWT + static API keys                      |

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for a detailed
explanation of the layered architecture (routers -> services -> integrations),
dependency injection, middleware pipeline, authentication design, and how
streaming, structured output, and function calling are implemented.

High-level request flow:

```
Client -> Middleware (CORS, Rate Limit, Logging, Auth Context)
       -> Router (validation via Pydantic)
       -> Service layer (business logic, prompt construction)
       -> AIService (OpenAI Responses API) / DatabaseService (SQLAlchemy)
       -> Response (Pydantic-validated JSON)
```

## Folder Structure

```
ai-rest-api/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── requirements.txt
├── pytest.ini
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── main.py # FastAPI app entrypoint
├── config.py # Settings (env-driven configuration)
├── database.py # SQLAlchemy engine/session
├── models.py # ORM models
├── schemas.py # Pydantic request/response models
├── dependencies.py # FastAPI DI providers
├── auth.py # API key + JWT auth utilities
├── logging_config.py # Loguru setup
├── routers/
│   ├── chat.py
│   ├── translate.py
│   ├── summarize.py
│   ├── email.py
│   ├── code.py
│   ├── prompt.py
│   └── health.py
├── services/
│   ├── ai_service.py # OpenAI Responses API wrapper
│   ├── chat_service.py
│   ├── translation_service.py
│   ├── summary_service.py
│   ├── email_service.py
│   ├── code_service.py
│   ├── prompt_service.py
│   └── database_service.py
├── middleware/
│   ├── authentication.py
│   ├── logging.py
│   ├── rate_limit.py
│   └── exceptions.py
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/0001_initial.py
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_auth.py
│   ├── test_chat.py
│   ├── test_translate.py
│   ├── test_summarize.py
│   ├── test_email.py
│   ├── test_code.py
│   └── test_prompt.py
└── docs/
    └── ARCHITECTURE.md
```

## Installation Guide

### 1. Install Python

Install **Python 3.12 or newer**:

- **Windows/macOS**: download from [python.org/downloads](https://www.python.org/downloads/)
- **macOS (Homebrew)**: `brew install python@3.12`
- **Ubuntu/Debian**: `sudo apt update && sudo apt install python3.12 python3.12-venv`

Verify the install:

```bash
python3 --version
```

### 2. Visual Studio Code Setup

1. Install [Visual Studio Code](https://code.visualstudio.com/).
2. Install the **Python** extension (Microsoft) from the Extensions
   marketplace (`Ctrl+Shift+X` / `Cmd+Shift+X`).
3. Optionally install **Pylance** (usually bundled with the Python
   extension) and **Ruff** or **Black** for linting/formatting.
4. Open the project folder: `File -> Open Folder... -> ai-rest-api`.
5. Once the virtual environment is created (next step), select it as the
   interpreter: `Ctrl+Shift+P` -> `Python: Select Interpreter` ->
   choose `./venv/bin/python` (or `.\venv\Scripts\python.exe` on Windows).

### 3. Create a Virtual Environment

From the project root:

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# Windows (cmd.exe)
python -m venv venv
venv\Scripts\activate.bat
```

You should see `(venv)` prefixed in your terminal prompt once activated.

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure `.env`

Copy the example environment file and fill in real values:

```bash
# macOS / Linux
cp .env.example .env

# Windows
copy .env.example .env
```

Open `.env` in VS Code and set, at minimum:

```
OPENAI_API_KEY=sk-your-real-key-here
API_KEY=some-strong-random-string
JWT_SECRET_KEY=another-strong-random-string
```

**Never commit `.env` to version control** - it is already listed in
`.gitignore`.

### 6. Obtaining an OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com/) and sign in
   or create an account.
2. Navigate to **API Keys** in the left sidebar (or
   `https://platform.openai.com/api-keys`).
3. Click **Create new secret key**, name it (e.g. `ai-rest-api-dev`), and
   copy the key immediately - it is only shown once.
4. Paste it into your `.env` file as `OPENAI_API_KEY`.
5. Ensure your OpenAI account has billing configured, since API usage is
   metered.

### 7. Database Setup

By default the app uses **SQLite** with zero configuration - a file named
`ai_rest_api.db` will be created automatically on first run in the project
root.

To use **PostgreSQL** instead, update `DATABASE_URL` in `.env`:

```
DATABASE_URL=postgresql://<user>:<password>@<host>:5432/<database_name>
```

Make sure the target database already exists (e.g.
`createdb ai_rest_api` for a local Postgres install) before running
migrations.

### 8. Running Alembic Migrations

The project ships with an initial migration that creates the
`conversations`, `messages`, and `api_usage_logs` tables.

```bash
# Apply all migrations (creates tables)
alembic upgrade head

# Roll back the last migration
alembic downgrade -1

# Generate a new migration after changing models.py
alembic revision --autogenerate -m "describe your change"
```

> Note: `main.py` also calls `init_db()` on startup for local development
> convenience, which will create tables directly from the SQLAlchemy
> models if they don't exist. In production, prefer managing schema
> changes exclusively through Alembic migrations.

### 9. Running the Server

```bash
uvicorn main:app --reload
```

Or run directly with Python:

```bash
python main.py
```

The API will be available at `http://localhost:8000`.

To run on a different host/port:

```bash
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

## API Authentication

Every AI endpoint (everything except `/`, `/health`, and `/version`) is
protected. Provide **either** of the following on each request:

**Option A - API Key**

```
X-API-Key: <your API_KEY from .env>
```

**Option B - Bearer Token (JWT)**

```
Authorization: Bearer <a JWT signed with your JWT_SECRET_KEY>
```

You can generate a test JWT in a Python shell:

```python
from auth import create_access_token
print(create_access_token(subject="my-client-id"))
```

Missing or invalid credentials return `401 Unauthorized` with a structured
error body.

## API Endpoints

| Method | Path                | Description                              | Auth required |
|--------|----------------------|-------------------------------------------|----------------|
| GET    | `/`                  | API root / discovery info                | No             |
| GET    | `/health`            | Health check (includes DB connectivity)  | No             |
| GET    | `/version`           | Version metadata                         | No             |
| POST   | `/chat`              | Conversational AI (supports streaming)   | Yes            |
| POST   | `/translate`         | Translate text                           | Yes            |
| POST   | `/summarize`         | Summarize text                           | Yes            |
| POST   | `/email`             | Generate an email draft                  | Yes            |
| POST   | `/code/explain`      | Explain a code snippet                   | Yes            |
| POST   | `/code/review`       | Structured code review                   | Yes            |
| POST   | `/code/refactor`     | Refactor code toward stated goals        | Yes            |
| POST   | `/prompt/improve`    | Rewrite a prompt to be clearer           | Yes            |
| POST   | `/prompt/optimize`   | Optimize a prompt for an objective       | Yes            |
| POST   | `/prompt/evaluate`   | Score prompt quality with feedback       | Yes            |

## Example Requests & Responses

### `POST /chat`

Request:

```json
{
  "message": "What is the capital of France?",
  "temperature": 0.7
}
```

Response (`200 OK`):

```json
{
  "conversation_id": "b3f1c2e4-...",
  "reply": "The capital of France is Paris.",
  "model": "gpt-4.1-mini",
  "usage": {"input_tokens": 24, "output_tokens": 9, "total_tokens": 33},
  "created_at": "2026-07-13T10:15:00Z"
}
```

### `POST /translate`

Request:

```json
{
  "text": "Good morning, how are you?",
  "target_language": "Spanish"
}
```

Response (`200 OK`):

```json
{
  "original_text": "Good morning, how are you?",
  "translated_text": "Buenos días, ¿cómo estás?",
  "source_language": "auto",
  "target_language": "Spanish",
  "model": "gpt-4.1-mini"
}
```

### `POST /code/review`

Request:

```json
{
  "code": "def divide(a, b):\n    return a / b",
  "language": "python",
  "focus_areas": ["error handling"]
}
```

Response (`200 OK`):

```json
{
  "summary": "The function does not guard against division by zero.",
  "issues": [
    {
      "severity": "high",
      "description": "No handling for b == 0, which raises ZeroDivisionError.",
      "suggestion": "Add an explicit check and raise a descriptive exception."
    }
  ],
  "language": "python",
  "model": "openai-responses-api"
}
```

## cURL Examples

```bash
# Health check (no auth)
curl http://localhost:8000/health

# Chat (API key auth)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"message": "Explain REST APIs in one sentence."}'

# Translate (Bearer token auth)
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"text": "Hello world", "target_language": "German"}'

# Streaming chat (Server-Sent Events)
curl -N -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"message": "Tell me a short story", "stream": true}'
```

## Postman Examples

1. Open Postman and create a new **Collection** named `ai-rest-api`.
2. Add a collection-level variable `base_url` = `http://localhost:8000`.
3. Add a collection-level **Authorization** of type **API Key**:
   - Key: `X-API-Key`
   - Value: `{{api_key}}` (define `api_key` as a collection variable)
   - Add to: **Header**
4. Create a new request: `POST {{base_url}}/chat`, Body -> raw -> JSON:
   ```json
   { "message": "Hi there" }
   ```
5. Send. You should receive a `200 OK` with a `reply` field.
6. Repeat for other endpoints using the paths in the
   [API Endpoints](#api-endpoints) table above.

You can also import the OpenAPI spec directly into Postman:
`File -> Import -> Link -> http://localhost:8000/openapi.json`.

## Swagger & ReDoc Documentation

Once the server is running:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
  - interactive, try-it-out documentation.
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
  - clean, reference-style documentation.
- **Raw OpenAPI spec**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## Testing

The test suite uses an in-memory SQLite database and mocks the AI service,
so it runs fast and requires no OpenAI API key or network access.

```bash
# Run the full test suite
pytest

# Run with verbose output (already default via pytest.ini)
pytest -v

# Run a specific test file
pytest tests/test_chat.py

# Run with coverage
pip install pytest-cov
pytest --cov=. --cov-report=term-missing
```

## Error Handling

All errors - whether from validation, authentication, the AI provider, or
unexpected server failures - return a consistent JSON envelope:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "message: field required"
  }
}
```

Common error codes:

| HTTP Status | Error Code             | Meaning                                  |
|-------------|--------------------------|--------------------------------------------|
| 401         | `UNAUTHORIZED`           | Missing/invalid API key or JWT             |
| 404         | `NOT_FOUND`              | e.g. unknown `conversation_id`             |
| 422         | `VALIDATION_ERROR`       | Request body failed Pydantic validation    |
| 429         | `RATE_LIMIT_EXCEEDED`    | Too many requests in the configured window |
| 502         | `AI_SERVICE_ERROR`       | The OpenAI API call failed                 |
| 500         | `INTERNAL_SERVER_ERROR`  | An unexpected server-side error            |

## Troubleshooting

**`OPENAI_API_KEY is not set` warning on startup**
Set `OPENAI_API_KEY` in your `.env` file. AI endpoints will return
`502 AI_SERVICE_ERROR` until a valid key is configured.

**`401 Unauthorized` on every request**
Ensure you're sending either `X-API-Key: <value matching API_KEY in .env>`
or a valid `Authorization: Bearer <jwt>` header.

**`sqlite3.OperationalError: unable to open database file`**
Ensure the process has write permission to the project directory (SQLite
needs to create the `.db` file there), or point `DATABASE_URL` at a
writable path.

**`ModuleNotFoundError` on startup**
Confirm your virtual environment is activated and
`pip install -r requirements.txt` completed without errors.

**Alembic: `Target database is not up to date`**
Run `alembic upgrade head` before starting the app, or delete the local
SQLite file and let `init_db()` recreate it (development only).

**CORS errors from a browser client**
Set `CORS_ORIGINS` in `.env` to a comma-separated list of allowed origins
(e.g. `http://localhost:3000,https://myapp.com`), or `*` for all origins
during local development.

**Rate limit (`429`) hit during testing**
Increase `RATE_LIMIT_REQUESTS` / `RATE_LIMIT_WINDOW_SECONDS` in `.env`, or
wait for the sliding window to reset.

## Deployment Guide

General steps for deploying to a VM, PaaS (Render/Railway/Fly.io), or
container platform:

1. Set `ENVIRONMENT=production` and `DEBUG=false` in your production
   environment configuration.
2. Provide a real `DATABASE_URL` pointing at a managed PostgreSQL instance.
3. Set strong, unique values for `API_KEY` and `JWT_SECRET_KEY` (e.g.
   `openssl rand -hex 32`).
4. Run `alembic upgrade head` as part of your deploy step, before starting
   the app server.
5. Run the app with a production ASGI process manager, e.g.:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```
6. Put a reverse proxy (Nginx, Caddy, or your platform's load balancer)
   in front of Uvicorn for TLS termination.
7. Restrict `CORS_ORIGINS` to your actual frontend domain(s).
8. Ship logs (`logs/app.log`, JSON-formatted) to your log aggregation
   platform of choice (e.g. Datadog, CloudWatch, ELK).

## Docker (optional)

Build and run with Docker directly:

```bash
docker build -t ai-rest-api .
docker run -p 8000:8000 --env-file .env ai-rest-api
```

Or use docker-compose (includes a PostgreSQL container):

```bash
docker compose up --build
```

This starts the API on `http://localhost:8000` backed by a PostgreSQL
container defined in `docker-compose.yml`.

## Future Improvements

- Add Redis-backed rate limiting and caching for multi-instance deployments
- Add refresh tokens and per-client API key management (currently a single
  static key)
- Add pagination to a future `GET /conversations` / `GET /conversations/{id}`
  endpoint for browsing chat history
- Add request-level retries with exponential backoff for transient OpenAI
  API errors
- Add OpenTelemetry tracing for distributed observability
- Add a `/code/generate` endpoint for generating code from a natural
  language spec
- Add role-based access control (RBAC) for multi-tenant deployments

## Contributing

1. Fork the repository and create a feature branch:
   `git checkout -b feature/my-improvement`
2. Install dependencies and set up pre-commit checks (formatting/linting
   of your choice, e.g. `black .` and `ruff check .`).
3. Write or update tests for any behavior change (`pytest` must pass).
4. Commit with a clear message and open a pull request describing the
   change and its motivation.

## License

Released under the [MIT License](LICENSE).

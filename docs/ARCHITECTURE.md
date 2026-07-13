# Architecture

This document explains the architectural decisions behind `ai-rest-api` and
the REST/backend principles it demonstrates.

## Why FastAPI

FastAPI was chosen over alternatives (Flask, Django REST Framework) for several reasons:

- **Native async support.** AI API calls are I/O-bound and can take
  seconds; FastAPI's `async def` route handlers let the server handle many
  concurrent requests without blocking worker threads.
- **Pydantic-first design.** Request and response validation is declared
  once, as Python types, and FastAPI automatically validates incoming
  payloads and serializes outgoing ones, eliminating a whole class of
  manual validation code and bugs.
- **Automatic OpenAPI generation.** Swagger UI (`/docs`) and ReDoc
  (`/redoc`) are generated directly from the route signatures and Pydantic
  models, so documentation cannot drift out of sync with the code.
- **Dependency injection system.** FastAPI's `Depends()` mechanism is a
  first-class, testable way to share database sessions, authentication
  logic, and services across routes (see below).
- **Performance.** Built on Starlette and Uvicorn (ASGI), FastAPI is
  among the fastest Python web frameworks available.

## REST API Principles Applied

- **Resource-oriented URLs**: `/chat`, `/translate`, `/summarize`, `/email`,
  `/code/explain`, `/prompt/improve`, etc. — each endpoint represents a
  distinct capability/resource.
- **HTTP methods carry meaning**: `GET` for read-only/idempotent operations
  (`/health`, `/version`), `POST` for operations that create a result or
  have side effects (all AI generation endpoints).
- **Meaningful status codes**: `200` success, `401` authentication failure,
  `404` missing resource (e.g. unknown `conversation_id`), `422` validation
  failure, `429` rate limit exceeded, `502` upstream AI provider failure,
  `500` unexpected server error.
- **Consistent envelope for errors**: every error response follows the
  same `{"success": false, "error": {"code": ..., "message": ...}}` shape,
  making client-side error handling uniform regardless of which endpoint
  failed or why.
- **Statelessness**: each request carries its own authentication
  credentials; server-side conversation state is explicit and addressed by
  `conversation_id`, not implicit session state.

## Layered Architecture

```
Client
  │
  ▼
Routers        (routers/*.py)      — HTTP concerns: paths, methods, status codes, docs
  │
  ▼
Services       (services/*.py)     — business logic, orchestration, prompt construction
  │
  ▼
AIService / DatabaseService        — external integrations: OpenAI API, SQLAlchemy
```

- **Routers** are intentionally thin. They parse/validate the request
  (via Pydantic), call a service method, and return the result. They
  contain no business logic.
- **Services** contain all business logic: how a prompt is constructed,
  how conversation history is assembled, how AI output is transformed
  into a response schema. Services are framework-agnostic — they don't
  know about `Request`/`Response` objects — which makes them independently
  unit-testable.
- **AIService** is the single integration point with OpenAI. Every other
  service depends on it rather than importing the OpenAI SDK directly,
  so provider-specific concerns (retries, error translation, schema
  formatting) live in exactly one place.

## Dependency Injection

FastAPI's `Depends()` is used throughout for:

- **Database sessions** (`Depends(get_db)`): a fresh SQLAlchemy `Session`
  per request, automatically closed afterward (see `database.py`).
- **Authentication** (`Depends(get_current_client)`): enforces that a
  valid API key or JWT bearer token is present before a protected route's
  body executes; centralizes auth logic instead of duplicating it in every
  route.
- **Shared services** (`Depends(get_ai_service)`): provides a singleton
  `AIService` instance so the OpenAI client isn't re-instantiated on every
  request.

This design also makes testing straightforward: `tests/conftest.py`
overrides `get_db` and `get_ai_service` with test doubles via
`app.dependency_overrides`, so tests never hit a real database or the real
OpenAI API.

## Middleware

Middleware is layered (outermost first, per `main.py`):

1. **CORSMiddleware** — controls which origins may call the API from a browser.
2. **RateLimitMiddleware** — a per-IP sliding-window limiter that returns
   `429 Too Many Requests` once a client exceeds its quota.
3. **RequestLoggingMiddleware** — logs every request/response pair with
   execution time, assigns a `X-Request-ID`, and persists a usage record.
4. **AuthContextMiddleware** — annotates the request with whether
   credentials were presented, for observability (does not itself block
   requests — actual enforcement is the `get_current_client` dependency).

## Pydantic & Validation

Every request body and response body is a Pydantic v2 model (see
`schemas.py`). Benefits:

- Type coercion and validation happen automatically before route code runs.
- Field-level constraints (`min_length`, `max_length`, `ge`/`le`, enums)
  express business rules declaratively.
- `response_model=` on every route guarantees the API never returns a
  shape that doesn't match its documented contract.
- The same models power OpenAPI schema generation — one source of truth.

## Authentication

Two schemes are supported simultaneously, and either is sufficient:

- **API Key** (`X-API-Key` header): simple shared-secret auth, suitable
  for server-to-server integrations.
- **Bearer JWT** (`Authorization: Bearer <token>`): stateless, signed
  tokens with expiration, suitable for user-scoped access. `auth.py`
  provides `create_access_token`/`decode_access_token` built on PyJWT.

Both are validated in the single `get_current_client` dependency
(`dependencies.py`), keeping enforcement logic in one auditable place.

## OpenAPI / Documentation

FastAPI generates a complete OpenAPI 3.1 specification from the route
definitions and Pydantic models automatically, exposed at `/openapi.json`,
and rendered interactively at `/docs` (Swagger UI) and `/redoc` (ReDoc).
No documentation is hand-written or maintained separately from the code.

## Streaming

The `/chat` endpoint supports `stream=true`, in which case the response is
a `text/event-stream` (Server-Sent Events) response. Internally,
`AIService.stream_text` wraps the OpenAI Responses API's streaming mode
and yields incremental text deltas as an `AsyncGenerator`, which
`ChatService.chat_stream` forwards to the client via FastAPI's
`StreamingResponse`.

## Structured Output

Several endpoints (`/email`, `/code/review`, `/code/refactor`,
`/prompt/improve`, `/prompt/optimize`, `/prompt/evaluate`) need the model
to return data in a precise shape (e.g. separate `subject`/`body` fields,
a list of typed issues). Rather than asking the model to "return JSON" in
prose and hoping it complies, `AIService.generate_structured` uses the
Responses API's `text.format = {"type": "json_schema", ...}` structured
output mode, which constrains the model's output to conform to a JSON
Schema. This eliminates parsing failures and prompt-injection-style
formatting drift.

## Function Calling

`AIService.call_with_tools` demonstrates the Responses API's function
calling / tool use capability: a list of callable tool definitions
(name, description, JSON Schema parameters) is passed alongside the
prompt, and the model may choose to emit one or more `function_call`
items instead of (or in addition to) plain text, which the caller is then
responsible for executing and (optionally) feeding back as tool results
in a follow-up turn.

## Conversation Context

`/chat` supports multi-turn conversations via `conversation_id`. On each
turn, `ChatService` loads prior messages for that conversation from the
database and prepends them to the prompt sent to the model, giving the
model full context without the client needing to resend the entire
history on every request. New conversations are created automatically
when no `conversation_id` is supplied.

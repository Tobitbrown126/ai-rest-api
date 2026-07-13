"""
schemas.py
----------
Pydantic v2 models used for request validation and response serialization
across every router in the application.

Keeping all schemas in one module makes it easy to see the full public
contract of the API at a glance, and avoids circular imports between
routers and services.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# ==========================================================================
# Shared / generic schemas
# ==========================================================================
class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["ok"])
    timestamp: datetime
    environment: str
    database: str


class VersionResponse(BaseModel):
    app_name: str
    version: str
    python_requires: str = ">=3.12"


class RootResponse(BaseModel):
    message: str
    docs_url: str
    redoc_url: str
    version: str


# ==========================================================================
# Chat schemas
# ==========================================================================
class ChatRole(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class ChatMessage(BaseModel):
    role: ChatRole
    content: str = Field(..., min_length=1, max_length=8000)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000, description="Latest user message")
    conversation_id: Optional[str] = Field(
        default=None, description="Existing conversation ID to continue, or omit to start new"
    )
    system_prompt: Optional[str] = Field(
        default=None,
        max_length=4000,
        description="Optional system prompt to steer model behavior",
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    stream: bool = Field(default=False, description="If true, response is streamed as SSE")
    max_output_tokens: int = Field(default=1024, ge=1, le=8000)

    @field_validator("message")
    @classmethod
    def strip_message(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("message cannot be empty or whitespace-only")
        return v


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    created_at: datetime


# ==========================================================================
# Translation schemas
# ==========================================================================
class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)
    target_language: str = Field(..., min_length=2, max_length=50, examples=["Spanish", "French"])
    source_language: Optional[str] = Field(default="auto")


class TranslateResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    model: str


# ==========================================================================
# Summarization schemas
# ==========================================================================
class SummaryLength(str, Enum):
    short = "short"
    medium = "medium"
    long = "long"


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)
    length: SummaryLength = Field(default=SummaryLength.medium)
    bullet_points: bool = Field(default=False)


class SummarizeResponse(BaseModel):
    summary: str
    original_length_chars: int
    summary_length_chars: int
    model: str


# ==========================================================================
# Email generation schemas
# ==========================================================================
class EmailTone(str, Enum):
    formal = "formal"
    casual = "casual"
    persuasive = "persuasive"
    friendly = "friendly"
    apologetic = "apologetic"


class EmailRequest(BaseModel):
    subject_hint: str = Field(..., min_length=1, max_length=300)
    key_points: List[str] = Field(..., min_length=1, max_length=20)
    tone: EmailTone = Field(default=EmailTone.formal)
    recipient_name: Optional[str] = Field(default=None, max_length=100)
    sender_name: Optional[str] = Field(default=None, max_length=100)


class EmailResponse(BaseModel):
    subject: str
    body: str
    tone: str
    model: str


# ==========================================================================
# Code assistance schemas
# ==========================================================================
class ProgrammingLanguage(str, Enum):
    python = "python"
    javascript = "javascript"
    typescript = "typescript"
    java = "java"
    csharp = "csharp"
    go = "go"
    rust = "rust"
    cpp = "cpp"
    other = "other"


class CodeExplainRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=20000)
    language: ProgrammingLanguage = Field(default=ProgrammingLanguage.python)


class CodeExplainResponse(BaseModel):
    explanation: str
    language: str
    model: str


class CodeReviewRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=20000)
    language: ProgrammingLanguage = Field(default=ProgrammingLanguage.python)
    focus_areas: Optional[List[str]] = Field(
        default=None, description="e.g. ['security', 'performance', 'readability']"
    )


class CodeIssue(BaseModel):
    severity: str = Field(..., examples=["low", "medium", "high", "critical"])
    description: str
    suggestion: str


class CodeReviewResponse(BaseModel):
    summary: str
    issues: List[CodeIssue]
    language: str
    model: str


class CodeRefactorRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=20000)
    language: ProgrammingLanguage = Field(default=ProgrammingLanguage.python)
    goals: Optional[List[str]] = Field(
        default=None, description="e.g. ['improve readability', 'reduce complexity']"
    )


class CodeRefactorResponse(BaseModel):
    refactored_code: str
    explanation_of_changes: str
    language: str
    model: str


# ==========================================================================
# Prompt engineering schemas
# ==========================================================================
class PromptImproveRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=8000)
    goal: Optional[str] = Field(default=None, max_length=500)


class PromptImproveResponse(BaseModel):
    original_prompt: str
    improved_prompt: str
    rationale: str
    model: str


class PromptOptimizeRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=8000)
    target_model: Optional[str] = Field(default=None, max_length=100)
    optimize_for: Optional[str] = Field(
        default="clarity", description="e.g. clarity, brevity, structured_output"
    )


class PromptOptimizeResponse(BaseModel):
    original_prompt: str
    optimized_prompt: str
    changes_made: List[str]
    model: str


class PromptEvaluateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=8000)


class PromptEvaluationScore(BaseModel):
    clarity: int = Field(..., ge=1, le=10)
    specificity: int = Field(..., ge=1, le=10)
    structure: int = Field(..., ge=1, le=10)
    overall: int = Field(..., ge=1, le=10)


class PromptEvaluateResponse(BaseModel):
    scores: PromptEvaluationScore
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    model: str


# ==========================================================================
# Auth schemas
# ==========================================================================
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int

"""create conversations, messages, api_usage_logs tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-01 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.String(length=36),
            sa.ForeignKey("conversations.id"),
            nullable=False,
        ),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])

    op.create_table(
        "api_usage_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("endpoint", sa.String(length=255), nullable=False),
        sa.Column("method", sa.String(length=10), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("execution_time_ms", sa.Float(), nullable=False),
        sa.Column("client_host", sa.String(length=64), nullable=True),
        sa.Column("request_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("api_usage_logs")
    op.drop_index("ix_messages_conversation_id", table_name="messages")
    op.drop_table("messages")
    op.drop_table("conversations")

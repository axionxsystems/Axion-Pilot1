"""
add_api_keys_and_rate_limit_tables

Revision ID: d4e3f2a1b6c7
Revises: c3f1a2b4d5e6
Create Date: 2026-05-14 12:00:00.000000

Creates api_keys and rate_limit_logs tables for API key authentication
and rate limiting functionality. Supports both PostgreSQL and SQLite.
"""

from __future__ import annotations
import sqlalchemy as sa
from alembic import op


revision      = "d4e3f2a1b6c7"
down_revision = "c3f1a2b4d5e6"
branch_labels = None
depends_on    = None


def _table_exists(conn, name: str) -> bool:
    return name in sa.inspect(conn).get_table_names()


def _col_exists(conn, table: str, col: str) -> bool:
    return any(c["name"] == col for c in sa.inspect(conn).get_columns(table))


def _index_exists(conn, table: str, index: str) -> bool:
    return any(i["name"] == index for i in sa.inspect(conn).get_indexes(table))


# ─────────────────────────────────────────────────────────────────────────────
def upgrade() -> None:
    conn = op.get_bind()

    # ── 1. api_keys table ─────────────────────────────────────────────────────
    if not _table_exists(conn, "api_keys"):
        op.create_table(
            "api_keys",
            sa.Column("id",                 sa.String(36),  primary_key=True),
            sa.Column("org_id",             sa.String(36),  nullable=False),
            sa.Column("created_by_user_id", sa.Integer(),   nullable=True),  # FK to users
            sa.Column("name",               sa.String(120), nullable=False),
            sa.Column("key_prefix",         sa.String(12),  nullable=False, index=True),  # First 12 chars for display
            sa.Column("key_hash",           sa.String(255), nullable=False),  # bcrypt hash
            sa.Column("scopes",             sa.JSON(),      nullable=False),  # ["read:projects", "write:projects"]
            sa.Column("rate_limit_rpm",     sa.Integer(),   nullable=False, server_default="1000"),  # Requests per minute
            sa.Column("created_at",         sa.DateTime(),  nullable=False,
                      server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("last_used_at",       sa.DateTime(),  nullable=True),  # Track usage
            sa.Column("expires_at",         sa.DateTime(),  nullable=True),  # Optional expiration
            sa.Column("active",             sa.Boolean(),   nullable=False, server_default="1"),  # Soft delete via active=false
        )
        
        # Indexes for common queries
        op.create_index("ix_api_keys_org_id_active", "api_keys", ["org_id", "active"])
        op.create_index("ix_api_keys_key_prefix",    "api_keys", ["key_prefix"])
        op.create_index("ix_api_keys_created_by",    "api_keys", ["created_by_user_id"])
        op.create_index("ix_api_keys_id",            "api_keys", ["id"])
        
        # Foreign key to organizations
        try:
            op.create_foreign_key(
                "fk_api_keys_org_id",
                "api_keys", "organizations",
                ["org_id"], ["id"],
                ondelete="CASCADE"
            )
        except Exception:
            pass  # Foreign key may already exist or be skipped in SQLite
        
        # Foreign key to users (optional, for audit)
        try:
            op.create_foreign_key(
                "fk_api_keys_created_by_user_id",
                "api_keys", "users",
                ["created_by_user_id"], ["id"],
                ondelete="SET NULL"
            )
        except Exception:
            pass

    # ── 2. rate_limit_logs table ──────────────────────────────────────────────
    if not _table_exists(conn, "rate_limit_logs"):
        op.create_table(
            "rate_limit_logs",
            sa.Column("id",         sa.String(36), primary_key=True),
            sa.Column("api_key_id", sa.String(36), nullable=False),  # FK to api_keys
            sa.Column("timestamp",  sa.DateTime(), nullable=False,
                      server_default=sa.text("CURRENT_TIMESTAMP"), index=True),
            sa.Column("request_count", sa.Integer(), nullable=False, server_default="1"),  # Requests in this minute
            sa.Column("minute_bucket", sa.String(20), nullable=False, index=True),  # E.g., "2026-05-14_12_30"
        )
        
        # Indexes for efficient lookups and cleanup
        op.create_index("ix_rate_limit_logs_api_key_id",   "rate_limit_logs", ["api_key_id"])
        op.create_index("ix_rate_limit_logs_timestamp",    "rate_limit_logs", ["timestamp"])
        op.create_index("ix_rate_limit_logs_minute_bucket", "rate_limit_logs", ["minute_bucket"])
        op.create_index("ix_rate_limit_logs_composite",    "rate_limit_logs", ["api_key_id", "timestamp"])
        
        # Foreign key to api_keys
        try:
            op.create_foreign_key(
                "fk_rate_limit_logs_api_key_id",
                "rate_limit_logs", "api_keys",
                ["api_key_id"], ["id"],
                ondelete="CASCADE"
            )
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
def downgrade() -> None:
    conn = op.get_bind()

    # Drop tables in reverse order (due to foreign keys)
    if _table_exists(conn, "rate_limit_logs"):
        op.drop_table("rate_limit_logs")
    
    if _table_exists(conn, "api_keys"):
        op.drop_table("api_keys")

"""
add_multitenancy_full_sqlite_compatible

Revision ID: c3f1a2b4d5e6
Revises: b9d3c4b1ade6
Create Date: 2026-05-12 00:30:00.000000

Creates organizations / subscriptions / audit_logs tables (SQLite-safe String(36)
UUIDs), then adds org_id + org_role to users and org_id to projects via
batch_alter_table. Fully reversible.
"""

from __future__ import annotations
import sqlalchemy as sa
from alembic import op

revision      = "c3f1a2b4d5e6"
down_revision = "b9d3c4b1ade6"
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

    # ── 1. organizations ──────────────────────────────────────────────────────
    if not _table_exists(conn, "organizations"):
        op.create_table(
            "organizations",
            sa.Column("id",         sa.String(36),  primary_key=True),
            sa.Column("name",       sa.String(120), nullable=False),
            sa.Column("slug",       sa.String(80),  nullable=False),
            sa.Column("tier",       sa.String(20),  nullable=False, server_default="free"),
            sa.Column("api_quota",  sa.Integer(),   nullable=False, server_default="100"),
            sa.Column("created_at", sa.DateTime(),  nullable=False,
                      server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("metadata",   sa.JSON(),      nullable=True),
        )
        op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=True)
        op.create_index("ix_organizations_id",   "organizations", ["id"])

    # ── 2. subscriptions ──────────────────────────────────────────────────────
    if not _table_exists(conn, "subscriptions"):
        op.create_table(
            "subscriptions",
            sa.Column("id",                     sa.String(36),  primary_key=True),
            sa.Column("org_id",                 sa.String(36),  nullable=False),
            sa.Column("stripe_subscription_id", sa.String(255), nullable=True),
            sa.Column("tier",                   sa.String(20),  nullable=False,
                      server_default="free"),
            sa.Column("status",                 sa.String(30),  nullable=False,
                      server_default="active"),
            sa.Column("next_billing_date",      sa.DateTime(),  nullable=True),
            sa.Column("usage_json",             sa.JSON(),      nullable=True),
            sa.Column("created_at",             sa.DateTime(),  nullable=False,
                      server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at",             sa.DateTime(),  nullable=True),
        )
        op.create_index("ix_subscriptions_org_id", "subscriptions", ["org_id"])
        op.create_index("ix_subscriptions_id",     "subscriptions", ["id"])

    # ── 3. audit_logs ─────────────────────────────────────────────────────────
    if not _table_exists(conn, "audit_logs"):
        op.create_table(
            "audit_logs",
            sa.Column("id",            sa.String(36),  primary_key=True),
            sa.Column("org_id",        sa.String(36),  nullable=False),
            sa.Column("actor_id",      sa.Integer(),   nullable=True),
            sa.Column("action",        sa.String(80),  nullable=False),
            sa.Column("resource_type", sa.String(80),  nullable=True),
            sa.Column("resource_id",   sa.String(120), nullable=True),
            sa.Column("changes",       sa.JSON(),      nullable=True),
            sa.Column("timestamp",     sa.DateTime(),  nullable=False,
                      server_default=sa.text("CURRENT_TIMESTAMP")),
        )
        op.create_index("ix_audit_logs_org_id",   "audit_logs", ["org_id"])
        op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"])
        op.create_index("ix_audit_logs_id",        "audit_logs", ["id"])

    # ── 4. users: org_id + org_role ───────────────────────────────────────────
    # batch_alter_table recreates the table, which sidesteps SQLite ALTER limits
    needs_users_batch = (
        not _col_exists(conn, "users", "org_id")
        or not _col_exists(conn, "users", "org_role")
    )
    if needs_users_batch:
        with op.batch_alter_table("users", schema=None) as b:
            if not _col_exists(conn, "users", "org_id"):
                b.add_column(sa.Column("org_id",   sa.String(36), nullable=True))
            if not _col_exists(conn, "users", "org_role"):
                b.add_column(sa.Column("org_role", sa.String(20), nullable=True,
                                       server_default="member"))

    if not _index_exists(conn, "users", "ix_users_org_id"):
        op.create_index("ix_users_org_id", "users", ["org_id"])

    # ── 5. projects: org_id + unique constraint ───────────────────────────────
    needs_projects_batch = not _col_exists(conn, "projects", "org_id")
    if needs_projects_batch:
        with op.batch_alter_table("projects", schema=None) as b:
            b.add_column(sa.Column("org_id", sa.String(36), nullable=True))
            b.create_unique_constraint("uq_org_project_title", ["org_id", "title"])

    if not _index_exists(conn, "projects", "ix_projects_org_id"):
        op.create_index("ix_projects_org_id", "projects", ["org_id"])


# ─────────────────────────────────────────────────────────────────────────────
def downgrade() -> None:
    conn = op.get_bind()

    # projects
    if _table_exists(conn, "projects") and _col_exists(conn, "projects", "org_id"):
        try:
            op.drop_index("ix_projects_org_id", table_name="projects")
        except Exception:
            pass
        with op.batch_alter_table("projects", schema=None) as b:
            try:
                b.drop_constraint("uq_org_project_title", type_="unique")
            except Exception:
                pass
            b.drop_column("org_id")

    # users
    if _table_exists(conn, "users"):
        try:
            op.drop_index("ix_users_org_id", table_name="users")
        except Exception:
            pass
        with op.batch_alter_table("users", schema=None) as b:
            if _col_exists(conn, "users", "org_role"):
                b.drop_column("org_role")
            if _col_exists(conn, "users", "org_id"):
                b.drop_column("org_id")

    # audit_logs
    if _table_exists(conn, "audit_logs"):
        for ix in ["ix_audit_logs_id", "ix_audit_logs_timestamp", "ix_audit_logs_org_id"]:
            try:
                op.drop_index(ix, table_name="audit_logs")
            except Exception:
                pass
        op.drop_table("audit_logs")

    # subscriptions
    if _table_exists(conn, "subscriptions"):
        for ix in ["ix_subscriptions_id", "ix_subscriptions_org_id"]:
            try:
                op.drop_index(ix, table_name="subscriptions")
            except Exception:
                pass
        op.drop_table("subscriptions")

    # organizations
    if _table_exists(conn, "organizations"):
        for ix in ["ix_organizations_id", "ix_organizations_slug"]:
            try:
                op.drop_index(ix, table_name="organizations")
            except Exception:
                pass
        op.drop_table("organizations")

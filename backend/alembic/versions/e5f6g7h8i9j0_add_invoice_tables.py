"""
add_invoice_tables

Revision ID: e5f6g7h8i9j0
Revises: d4e3f2a1b6c7
Create Date: 2026-06-19 12:00:00.000000

Adds invoice accounting fields to stripe_invoices and creates invoice_line_items
and invoice_payments tables for line-item accounting and receipt tracking.
"""

from __future__ import annotations
import sqlalchemy as sa
from alembic import op


revision = "e5f6g7h8i9j0"
down_revision = "d4e3f2a1b6c7"
branch_labels = None
depends_on = None


def _table_exists(conn, name: str) -> bool:
    return name in sa.inspect(conn).get_table_names()


def _col_exists(conn, table: str, col: str) -> bool:
    return any(c["name"] == col for c in sa.inspect(conn).get_columns(table))


# ─────────────────────────────────────────────────────────────────────────────
def upgrade() -> None:
    conn = op.get_bind()

    if _table_exists(conn, "stripe_invoices"):
        if not _col_exists(conn, "stripe_invoices", "subtotal"):
            op.add_column(
                "stripe_invoices",
                sa.Column("subtotal", sa.Integer(), nullable=False, server_default="0"),
            )

        if not _col_exists(conn, "stripe_invoices", "tax_rate"):
            op.add_column(
                "stripe_invoices",
                sa.Column("tax_rate", sa.Float(), nullable=False, server_default="0.0"),
            )

        if not _col_exists(conn, "stripe_invoices", "tax_amount"):
            op.add_column(
                "stripe_invoices",
                sa.Column("tax_amount", sa.Integer(), nullable=False, server_default="0"),
            )

        if not _col_exists(conn, "stripe_invoices", "total"):
            op.add_column(
                "stripe_invoices",
                sa.Column("total", sa.Integer(), nullable=False, server_default="0"),
            )

        if not _col_exists(conn, "stripe_invoices", "pdf_path"):
            op.add_column(
                "stripe_invoices",
                sa.Column("pdf_path", sa.String(255), nullable=True),
            )

        if not _col_exists(conn, "stripe_invoices", "invoice_number"):
            op.add_column(
                "stripe_invoices",
                sa.Column("invoice_number", sa.String(100), nullable=True),
            )

    if not _table_exists(conn, "invoice_line_items"):
        op.create_table(
            "invoice_line_items",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("invoice_id", sa.String(36), nullable=False, index=True),
            sa.Column("description", sa.Text(), nullable=False, server_default=""),
            sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("unit_price", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("amount", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("tax_rate", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("tax_amount", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )
        try:
            op.create_foreign_key(
                "fk_invoice_line_items_invoice_id",
                "invoice_line_items", "stripe_invoices",
                ["invoice_id"], ["id"],
                ondelete="CASCADE",
            )
        except Exception:
            pass

    if not _table_exists(conn, "invoice_payments"):
        op.create_table(
            "invoice_payments",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("invoice_id", sa.String(36), nullable=False, index=True),
            sa.Column("stripe_payment_intent_id", sa.String(255), nullable=True, index=True),
            sa.Column("amount", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("currency", sa.String(3), nullable=False, server_default="usd"),
            sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
            sa.Column("paid_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )
        try:
            op.create_foreign_key(
                "fk_invoice_payments_invoice_id",
                "invoice_payments", "stripe_invoices",
                ["invoice_id"], ["id"],
                ondelete="CASCADE",
            )
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
def downgrade() -> None:
    conn = op.get_bind()

    if _table_exists(conn, "invoice_payments"):
        op.drop_table("invoice_payments")

    if _table_exists(conn, "invoice_line_items"):
        op.drop_table("invoice_line_items")

    if _table_exists(conn, "stripe_invoices"):
        if _col_exists(conn, "stripe_invoices", "invoice_number"):
            op.drop_column("stripe_invoices", "invoice_number")
        if _col_exists(conn, "stripe_invoices", "pdf_path"):
            op.drop_column("stripe_invoices", "pdf_path")
        if _col_exists(conn, "stripe_invoices", "total"):
            op.drop_column("stripe_invoices", "total")
        if _col_exists(conn, "stripe_invoices", "tax_amount"):
            op.drop_column("stripe_invoices", "tax_amount")
        if _col_exists(conn, "stripe_invoices", "tax_rate"):
            op.drop_column("stripe_invoices", "tax_rate")
        if _col_exists(conn, "stripe_invoices", "subtotal"):
            op.drop_column("stripe_invoices", "subtotal")

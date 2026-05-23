"""user contact fields (email, phone, full_name) + lockout + password_reset_tokens

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-23 16:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # User-Felder
    op.add_column("user", sa.Column("email", sa.String(255), nullable=True))
    op.add_column("user", sa.Column("phone", sa.String(64), nullable=True))
    op.add_column("user", sa.Column("full_name", sa.String(255), nullable=True))
    op.add_column(
        "user",
        sa.Column("failed_login_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("user", sa.Column("locked_until", sa.DateTime(), nullable=True))
    # Eindeutiger Index auf email (nullable – MariaDB erlaubt mehrere NULLs in UNIQUE)
    op.create_index("ix_user_email", "user", ["email"], unique=True)

    # Passwort-Reset-Tokens
    op.create_table(
        "password_reset_token",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("token_hash", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("requesting_ip", sa.String(64), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash", name="uq_password_reset_token_hash"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    op.create_index(
        "ix_password_reset_user_used",
        "password_reset_token",
        ["user_id", "used_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_password_reset_user_used", table_name="password_reset_token")
    op.drop_table("password_reset_token")
    op.drop_index("ix_user_email", table_name="user")
    op.drop_column("user", "locked_until")
    op.drop_column("user", "failed_login_count")
    op.drop_column("user", "full_name")
    op.drop_column("user", "phone")
    op.drop_column("user", "email")

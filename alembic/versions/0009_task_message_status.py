"""task_message_status: Status-Ampel auf Task/Message, vehicle_id auf Message, MessageSuggestion

Revision ID: 0009
Revises: 0008
Create Date: 2026-05-23 21:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("task", sa.Column("status", sa.String(20), nullable=False, server_default="open"))
    op.add_column("message", sa.Column("status", sa.String(20), nullable=False, server_default="open"))
    op.add_column(
        "message",
        sa.Column(
            "vehicle_id",
            sa.BigInteger(),
            sa.ForeignKey("incident_vehicle.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_table(
        "message_suggestion",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("alarm_type_code", sa.String(10), nullable=False),
        sa.Column("text", sa.String(500), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["alarm_type_code"], ["alarm_type.code"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )


def downgrade() -> None:
    op.drop_table("message_suggestion")
    op.drop_column("message", "vehicle_id")
    op.drop_column("message", "status")
    op.drop_column("task", "status")

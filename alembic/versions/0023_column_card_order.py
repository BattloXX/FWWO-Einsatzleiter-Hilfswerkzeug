"""incident_column: card_order JSON für spaltenübergreifende Reihenfolge

Revision ID: 0023
Revises: 0022
Create Date: 2026-05-29 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect as sa_inspect

revision = "0023"
down_revision = "0022"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    insp = sa_inspect(conn)
    cols = [c["name"] for c in insp.get_columns("incident_column")]
    if "card_order" not in cols:
        with op.batch_alter_table("incident_column", schema=None) as batch_op:
            batch_op.add_column(sa.Column("card_order", sa.Text, nullable=True))


def downgrade():
    with op.batch_alter_table("incident_column", schema=None) as batch_op:
        batch_op.drop_column("card_order")

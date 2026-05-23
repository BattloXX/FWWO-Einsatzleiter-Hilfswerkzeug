"""unit_bos_and_status: BOS-Feld auf FireDept/VehicleMaster, unit_status auf IncidentVehicle

Revision ID: 0008
Revises: 0007
Create Date: 2026-05-23 20:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("fire_dept", sa.Column("bos", sa.String(20), nullable=False, server_default="Feuerwehr"))
    op.add_column("vehicle_master", sa.Column("bos_override", sa.String(20), nullable=True))
    op.add_column(
        "incident_vehicle",
        sa.Column("unit_status", sa.String(40), nullable=False, server_default="Einsatz übernommen"),
    )


def downgrade() -> None:
    op.drop_column("incident_vehicle", "unit_status")
    op.drop_column("vehicle_master", "bos_override")
    op.drop_column("fire_dept", "bos")

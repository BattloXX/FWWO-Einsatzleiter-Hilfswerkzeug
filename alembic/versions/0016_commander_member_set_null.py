"""Model-Fix: commander_member_id ondelete=SET NULL (DB hatte das schon seit 0001)

Revision ID: 0016
Revises: 0015
Create Date: 2026-05-25 21:00:00.000000

Hintergrund: incident_vehicle.commander_member_id wurde in 0001 bereits mit
ON DELETE SET NULL angelegt. Das SQLAlchemy-Model hatte das Attribut aber nicht
gesetzt, weshalb ORM-seitige Cascade-Logik falsch lief. Diese Migration ist ein
reiner Revisions-Bump — kein DDL nötig.
"""


revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass  # DDL already correct since 0001; only ORM model was updated.


def downgrade() -> None:
    pass

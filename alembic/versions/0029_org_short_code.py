"""fire_dept: short_code (3-Zeichen-Kuerzel fuer Fahrzeugdarstellung, z.B. WOL)

Revision ID: 0029
Revises: 0028
Create Date: 2026-05-30
"""
from alembic import op
from sqlalchemy import text

revision = "0029"
down_revision = "0028"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(text("""
        ALTER TABLE `fire_dept`
        ADD COLUMN IF NOT EXISTS `short_code` VARCHAR(3) NULL
    """))


def downgrade():
    op.execute(text("ALTER TABLE `fire_dept` DROP COLUMN IF EXISTS `short_code`"))

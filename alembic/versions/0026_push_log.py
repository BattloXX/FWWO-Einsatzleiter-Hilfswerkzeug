"""Push-Log Tabelle: protokolliert alle gesendeten Push-Nachrichten

Revision ID: 0026
Revises: 0025
Create Date: 2026-05-29
"""
from alembic import op
from sqlalchemy import text

revision = "0026"
down_revision = "0025"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(text("""
        CREATE TABLE IF NOT EXISTS `push_log` (
            `id`             BIGINT        NOT NULL AUTO_INCREMENT,
            `sent_at`        DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `title`          VARCHAR(255)  NOT NULL,
            `body`           TEXT          NOT NULL,
            `url`            VARCHAR(500)  NULL,
            `source`         VARCHAR(50)   NOT NULL DEFAULT 'system',
            `target_user_id` BIGINT        NULL,
            `sent_count`     INT           NOT NULL DEFAULT 0,
            `total_count`    INT           NOT NULL DEFAULT 0,
            PRIMARY KEY (`id`),
            CONSTRAINT `fk_push_log_user`
                FOREIGN KEY (`target_user_id`) REFERENCES `user`(`id`)
                ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """))


def downgrade():
    op.execute(text("DROP TABLE IF EXISTS `push_log`"))

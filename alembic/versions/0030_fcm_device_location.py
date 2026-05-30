"""fcm_token Tabelle + DeviceToken Standort-Spalten fuer native Android-App

Revision ID: 0030
Revises: 0029
Create Date: 2026-05-30
"""
from alembic import op
from sqlalchemy import text

revision = "0030"
down_revision = "0029"
branch_labels = None
depends_on = None


def upgrade():
    # Neue Tabelle fcm_token fuer native FCM-Push-Tokens der Android-App
    op.execute(text("""
        CREATE TABLE IF NOT EXISTS `fcm_token` (
            `id`              BIGINT        NOT NULL AUTO_INCREMENT,
            `user_id`         BIGINT        NOT NULL,
            `device_token_id` BIGINT        NULL,
            `token`           VARCHAR(512)  NOT NULL,
            `platform`        VARCHAR(20)   NOT NULL DEFAULT 'android',
            `created_at`      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `last_used_at`    DATETIME      NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `uq_fcm_token` (`token`),
            CONSTRAINT `fk_fcm_token_user`
                FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
            CONSTRAINT `fk_fcm_token_device`
                FOREIGN KEY (`device_token_id`) REFERENCES `device_token`(`id`) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """))

    # GPS-Standort-Spalten auf device_token fuer Lagekarte
    op.execute(text("""
        ALTER TABLE `device_token`
        ADD COLUMN IF NOT EXISTS `last_lat`         DOUBLE NULL,
        ADD COLUMN IF NOT EXISTS `last_lng`         DOUBLE NULL,
        ADD COLUMN IF NOT EXISTS `last_location_at` DATETIME NULL,
        ADD COLUMN IF NOT EXISTS `duty_active`      TINYINT(1) NOT NULL DEFAULT 0
    """))


def downgrade():
    op.execute(text("DROP TABLE IF EXISTS `fcm_token`"))
    op.execute(text("""
        ALTER TABLE `device_token`
        DROP COLUMN IF EXISTS `duty_active`,
        DROP COLUMN IF EXISTS `last_location_at`,
        DROP COLUMN IF EXISTS `last_lng`,
        DROP COLUMN IF EXISTS `last_lat`
    """))

"""initial

Revision ID: 0001
Revises:
Create Date: 2026-05-22 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # fire_dept
    op.create_table(
        "fire_dept",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("slug", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("color", sa.String(7), nullable=False, server_default="#b71921"),
        sa.Column("withdraw_press_factor", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("withdraw_press_reserve", sa.Float(), nullable=False, server_default="10.0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # vehicle_master
    op.create_table(
        "vehicle_master",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("dept_id", sa.BigInteger(), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("type", sa.String(50), nullable=True),
        sa.Column("is_first_train", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["dept_id"], ["fire_dept.id"]),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # qualification
    op.create_table(
        "qualification",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # member
    op.create_table(
        "member",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("lastname", sa.String(100), nullable=False),
        sa.Column("firstname", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("email", sa.String(200), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # member_qualification
    op.create_table(
        "member_qualification",
        sa.Column("member_id", sa.BigInteger(), nullable=False),
        sa.Column("qualification_id", sa.BigInteger(), nullable=False),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(["member_id"], ["member.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["qualification_id"], ["qualification.id"]),
        sa.PrimaryKeyConstraint("member_id", "qualification_id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # alarm_type
    op.create_table(
        "alarm_type",
        sa.Column("code", sa.String(10), nullable=False),
        sa.Column("category", sa.String(20), nullable=False),
        sa.Column("default_first_train_only", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("notify_neighbors", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("code"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # task_suggestion
    op.create_table(
        "task_suggestion",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("alarm_type_code", sa.String(10), nullable=False),
        sa.Column("text", sa.String(500), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["alarm_type_code"], ["alarm_type.code"]),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # lage_hint
    op.create_table(
        "lage_hint",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("text", sa.String(500), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # default_message
    op.create_table(
        "default_message",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("alarm_type_code", sa.String(10), nullable=False),
        sa.Column("text", sa.String(500), nullable=False),
        sa.Column("due_after_sec", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["alarm_type_code"], ["alarm_type.code"]),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # role
    op.create_table(
        "role",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # user
    op.create_table(
        "user",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("password_hash", sa.String(200), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # user_role
    op.create_table(
        "user_role",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("role_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["role.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # api_key
    op.create_table(
        "api_key",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("key_hash", sa.String(200), nullable=False),
        sa.Column("label", sa.String(200), nullable=False),
        sa.Column("created_by_user_id", sa.BigInteger(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # audit_log
    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("api_key_id", sa.BigInteger(), nullable=True),
        sa.Column("incident_id", sa.BigInteger(), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=True),
        sa.Column("entity_id", sa.BigInteger(), nullable=True),
        sa.Column("payload_json", sa.Text(), nullable=True),
        sa.Column("ip", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["api_key_id"], ["api_key.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # push_subscription
    op.create_table(
        "push_subscription",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("endpoint", sa.Text(), nullable=False),
        sa.Column("p256dh", sa.Text(), nullable=False),
        sa.Column("auth", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # incident
    op.create_table(
        "incident",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("external_key", sa.String(200), nullable=True),
        sa.Column("nummer", sa.Integer(), nullable=True),
        sa.Column("alarm_type_code", sa.String(10), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.Column("incident_leader_user_id", sa.BigInteger(), nullable=True),
        sa.Column("is_exercise", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("address_street", sa.String(200), nullable=True),
        sa.Column("address_no", sa.String(20), nullable=True),
        sa.Column("address_city", sa.String(100), nullable=True),
        sa.Column("report_text", sa.Text(), nullable=True),
        sa.Column("reason", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["alarm_type_code"], ["alarm_type.code"]),
        sa.ForeignKeyConstraint(["incident_leader_user_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_key"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # incident_column
    op.create_table(
        "incident_column",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("incident_id", sa.BigInteger(), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("is_fixed", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["incident_id"], ["incident.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # incident_vehicle
    op.create_table(
        "incident_vehicle",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("incident_id", sa.BigInteger(), nullable=False),
        sa.Column("column_id", sa.BigInteger(), nullable=True),
        sa.Column("vehicle_master_id", sa.BigInteger(), nullable=False),
        sa.Column("commander_member_id", sa.BigInteger(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("removed_at", sa.DateTime(), nullable=True),
        sa.Column("org_color_override", sa.String(7), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["incident_id"], ["incident.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["column_id"], ["incident_column.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["vehicle_master_id"], ["vehicle_master.id"]),
        sa.ForeignKeyConstraint(["commander_member_id"], ["member.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # task
    op.create_table(
        "task",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("incident_id", sa.BigInteger(), nullable=False),
        sa.Column("column_id", sa.BigInteger(), nullable=True),
        sa.Column("vehicle_id", sa.BigInteger(), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("is_done", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("done_at", sa.DateTime(), nullable=True),
        sa.Column("is_cancelled", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["incident_id"], ["incident.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["column_id"], ["incident_column.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["vehicle_id"], ["incident_vehicle.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # message
    op.create_table(
        "message",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("incident_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("due_after_sec", sa.Integer(), nullable=True),
        sa.Column("due_at", sa.DateTime(), nullable=True),
        sa.Column("popup_shown", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("is_done", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("is_cancelled", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["incident_id"], ["incident.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # rescued_person
    op.create_table(
        "rescued_person",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("incident_id", sa.BigInteger(), nullable=False),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("person_group", sa.String(50), nullable=True),
        sa.Column("age_range", sa.String(50), nullable=True),
        sa.Column("name", sa.String(200), nullable=True),
        sa.Column("location", sa.String(500), nullable=True),
        sa.Column("vehicle_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["incident_id"], ["incident.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vehicle_id"], ["incident_vehicle.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # incident_log
    op.create_table(
        "incident_log",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("incident_id", sa.BigInteger(), nullable=False),
        sa.Column("ts", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("level", sa.String(10), nullable=False, server_default="info"),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=True),
        sa.Column("entity_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["incident_id"], ["incident.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # incident_change
    op.create_table(
        "incident_change",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("incident_id", sa.BigInteger(), nullable=False),
        sa.Column("ts", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.BigInteger(), nullable=True),
        sa.Column("before_json", sa.Text(), nullable=True),
        sa.Column("after_json", sa.Text(), nullable=True),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("api_key_id", sa.BigInteger(), nullable=True),
        sa.Column("ip", sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(["incident_id"], ["incident.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["api_key_id"], ["api_key.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # incident_token
    op.create_table(
        "incident_token",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("incident_id", sa.BigInteger(), nullable=False),
        sa.Column("token_hash", sa.String(200), nullable=False),
        sa.Column("issued_by_user_id", sa.BigInteger(), nullable=True),
        sa.Column("target_user_id", sa.BigInteger(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["incident_id"], ["incident.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["issued_by_user_id"], ["user.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["target_user_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # breathing_troop
    op.create_table(
        "breathing_troop",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("incident_id", sa.BigInteger(), nullable=False),
        sa.Column("vehicle_id", sa.BigInteger(), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="bereit"),
        sa.Column("task_text", sa.String(500), nullable=True),
        sa.Column("start_press_avg", sa.Float(), nullable=True),
        sa.Column("entry_at", sa.DateTime(), nullable=True),
        sa.Column("withdraw_press_calc", sa.Float(), nullable=True),
        sa.Column("withdraw_at", sa.DateTime(), nullable=True),
        sa.Column("back_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["incident_id"], ["incident.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vehicle_id"], ["incident_vehicle.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # troop_member
    op.create_table(
        "troop_member",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("troop_id", sa.BigInteger(), nullable=False),
        sa.Column("member_id", sa.BigInteger(), nullable=True),
        sa.Column("free_text_name", sa.String(200), nullable=True),
        sa.Column("role", sa.String(30), nullable=False, server_default="truppmann"),
        sa.Column("start_press", sa.Float(), nullable=True),
        sa.Column("withdraw_press", sa.Float(), nullable=True),
        sa.Column("back_press", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["troop_id"], ["breathing_troop.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["member_id"], ["member.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )

    # pressure_log
    op.create_table(
        "pressure_log",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("troop_id", sa.BigInteger(), nullable=False),
        sa.Column("ts", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("member_id", sa.BigInteger(), nullable=True),
        sa.Column("pressure_bar", sa.Float(), nullable=False),
        sa.Column("recorded_by_user_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["troop_id"], ["breathing_troop.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["member_id"], ["member.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["recorded_by_user_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )


def downgrade() -> None:
    op.drop_table("pressure_log")
    op.drop_table("troop_member")
    op.drop_table("breathing_troop")
    op.drop_table("incident_token")
    op.drop_table("incident_change")
    op.drop_table("incident_log")
    op.drop_table("rescued_person")
    op.drop_table("message")
    op.drop_table("task")
    op.drop_table("incident_vehicle")
    op.drop_table("incident_column")
    op.drop_table("incident")
    op.drop_table("push_subscription")
    op.drop_table("audit_log")
    op.drop_table("api_key")
    op.drop_table("user_role")
    op.drop_table("user")
    op.drop_table("role")
    op.drop_table("default_message")
    op.drop_table("lage_hint")
    op.drop_table("task_suggestion")
    op.drop_table("alarm_type")
    op.drop_table("member_qualification")
    op.drop_table("member")
    op.drop_table("qualification")
    op.drop_table("vehicle_master")
    op.drop_table("fire_dept")

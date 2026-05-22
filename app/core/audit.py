from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session


def write_audit(
    db: Session,
    action: str,
    *,
    user_id: Optional[int] = None,
    api_key_id: Optional[int] = None,
    incident_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    payload: Optional[dict] = None,
    ip: Optional[str] = None,
) -> None:
    """Write a system-level audit log entry (auth, admin actions, API-key usage)."""
    import json
    from app.models.user import AuditLog

    entry = AuditLog(
        action=action,
        user_id=user_id,
        api_key_id=api_key_id,
        incident_id=incident_id,
        entity_type=entity_type,
        entity_id=entity_id,
        payload_json=json.dumps(payload, ensure_ascii=False, default=str) if payload else None,
        ip=ip,
        created_at=datetime.now(timezone.utc),
    )
    db.add(entry)
    # caller is responsible for commit


def write_incident_change(
    db: Session,
    incident_id: int,
    action: str,
    entity_type: str,
    entity_id: int,
    before: Optional[dict],
    after: Optional[dict],
    *,
    user_id: Optional[int] = None,
    api_key_id: Optional[int] = None,
    ip: Optional[str] = None,
) -> None:
    """Write a granular incident change record (every field mutation)."""
    import json
    from app.models.incident import IncidentChange

    entry = IncidentChange(
        incident_id=incident_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before_json=json.dumps(before, ensure_ascii=False, default=str) if before else None,
        after_json=json.dumps(after, ensure_ascii=False, default=str) if after else None,
        user_id=user_id,
        api_key_id=api_key_id,
        ip=ip,
        ts=datetime.now(timezone.utc),
    )
    db.add(entry)

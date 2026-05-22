"""Externe REST-API – Einsatz automatisch anlegen."""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import hash_api_key
from app.core.audit import write_audit
from app.models.user import ApiKey
from app.models.incident import Incident
from app.services.incident_service import create_incident
from app.services.broadcast import manager
from app.services.push_service import notify_all
from app.config import settings

router = APIRouter(prefix="/api/v1", tags=["API v1"])

# Mapping of possible lowercase Stufe values to alarm type codes
STUFE_MAP = {
    "f1": "F1", "f2": "F2", "f3": "F3", "f4": "F4", "f14": "F14",
    "t1": "T1", "t2": "T2", "t3": "T3", "t4": "T4", "t6": "T6", "t7": "T7",
    # Numeric variants
    "1": "T1", "2": "T2", "3": "T3", "4": "T4", "6": "T6", "7": "T7",
    "t9": "T3",  # fallback for unknown T-variants
}


class AlarmPayload(BaseModel):
    Key: str
    Nummer: Optional[int] = None
    AlarmDatumZeit: Optional[str] = None
    Stufe: Optional[str] = None
    Art: Optional[str] = None
    Meldung: Optional[str] = None
    Einsatzgrund: Optional[str] = None
    Ort: Optional[str] = None
    Strasse: Optional[str] = None
    HausNr: Optional[str] = None
    Uebung: bool = False


def _get_api_key(x_api_key: str = Header(..., alias="X-API-Key"), db: Session = Depends(get_db)):
    key_hash = hash_api_key(x_api_key)
    api_key = db.query(ApiKey).filter(ApiKey.key_hash == key_hash).first()
    if not api_key or not api_key.is_active:
        raise HTTPException(status_code=401, detail="Ungültiger oder gesperrter API-Key")
    api_key.last_used_at = datetime.now(timezone.utc)
    return api_key


@router.post("/einsatz")
async def create_incident_api(
    payload: AlarmPayload,
    request: Request,
    db: Session = Depends(get_db),
    api_key: ApiKey = Depends(_get_api_key),
):
    # Idempotency check
    existing = db.query(Incident).filter(Incident.external_key == payload.Key).first()
    if existing:
        write_audit(db, "api.incident.duplicate", api_key_id=api_key.id,
                    incident_id=existing.id, ip=request.client.host if request.client else None)
        db.commit()
        return {"id": existing.id, "external_key": existing.external_key,
                "url": f"/einsatz/{existing.id}", "created": False}

    # Map Stufe to alarm type code
    stufe_raw = (payload.Stufe or "T1").lower().strip()
    alarm_type_code = STUFE_MAP.get(stufe_raw, "T1")

    # Parse AlarmDatumZeit
    started_at = None
    if payload.AlarmDatumZeit:
        try:
            started_at = datetime.fromisoformat(payload.AlarmDatumZeit)
            if started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=timezone.utc)
        except ValueError:
            started_at = None

    incident = create_incident(
        db,
        alarm_type_code=alarm_type_code,
        started_at=started_at,
        external_key=payload.Key,
        nummer=payload.Nummer,
        is_exercise=payload.Uebung,
        address_street=payload.Strasse,
        address_no=payload.HausNr,
        address_city=payload.Ort,
        report_text=payload.Meldung,
        reason=payload.Einsatzgrund,
        api_key_id=api_key.id,
        ip=request.client.host if request.client else None,
    )
    db.commit()

    address = f"{payload.Strasse or ''} {payload.HausNr or ''}, {payload.Ort or ''}".strip(", ")
    exercise_prefix = "[ÜBUNG] " if payload.Uebung else ""

    # WebSocket broadcast to all connected clients
    await manager.broadcast_all({
        "type": "incident_created",
        "incident_id": incident.id,
        "alarm": alarm_type_code,
        "address": address,
        "is_exercise": payload.Uebung,
        "url": f"/einsatz/{incident.id}",
        "title": f"{exercise_prefix}Neuer Einsatz: {alarm_type_code} – {address}",
    })

    # Web Push notification
    push_title = f"{exercise_prefix}🚒 Einsatz: {alarm_type_code}"
    push_body = address or payload.Meldung or "Kein Ort angegeben"
    notify_all(db, push_title, push_body, url=f"/einsatz/{incident.id}")

    return {
        "id": incident.id,
        "external_key": incident.external_key,
        "url": f"/einsatz/{incident.id}",
        "created": True,
    }


@router.get("/einsatz/active")
def list_active_incidents(db: Session = Depends(get_db), api_key: ApiKey = Depends(_get_api_key)):
    incidents = db.query(Incident).filter(Incident.status == "active").all()
    return [{"id": i.id, "alarm_type_code": i.alarm_type_code,
             "started_at": i.started_at, "is_exercise": i.is_exercise} for i in incidents]


@router.get("/einsatz/{incident_id}")
def get_incident(incident_id: int, db: Session = Depends(get_db), api_key: ApiKey = Depends(_get_api_key)):
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404)
    return {
        "id": incident.id,
        "alarm_type_code": incident.alarm_type_code,
        "status": incident.status,
        "started_at": incident.started_at,
        "address": f"{incident.address_street or ''} {incident.address_no or ''}, {incident.address_city or ''}".strip(", "),
        "is_exercise": incident.is_exercise,
    }

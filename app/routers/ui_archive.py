"""Archiv & PDF-Export.

Org-Scoping:
- Listen und Detailansichten werden nach Org gefiltert; system_admin sieht alles.
- Endpoints können nur eigene oder mitwirkende Org-Einsätze abrufen.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.permissions import can_access_incident
from app.db import get_db
from app.models.incident import Incident, IncidentOrg
from app.services.pdf_service import render_incident_pdf

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _scoped_incidents_query(db: Session, user):
    """Liefert eine Incident-Query, die nur Einsätze enthält, die der User sehen darf."""
    q = db.query(Incident)
    user_role_codes = {r.code for r in user.roles}
    if "system_admin" in user_role_codes:
        return q
    if user.org_id is None:
        # Kein Org, kein system_admin → keine Einsätze
        return q.filter(Incident.id == None)  # noqa: E711  → leeres Resultset
    collab_ids_subq = db.query(IncidentOrg.incident_id).filter(
        IncidentOrg.org_id == user.org_id
    )
    return q.filter(
        or_(
            Incident.primary_org_id == user.org_id,
            Incident.id.in_(collab_ids_subq),
        )
    )


@router.get("/archiv", response_class=HTMLResponse)
async def archive_list(request: Request, db: Session = Depends(get_db)):
    user = getattr(request.state, "user", None)
    if not user:
        return RedirectResponse("/login", status_code=302)
    incidents = _scoped_incidents_query(db, user).order_by(Incident.started_at.desc()).all()
    return templates.TemplateResponse(request, "archive/list.html", {
        "user": user, "incidents": incidents,
    })


@router.get("/archiv/{incident_id}", response_class=HTMLResponse)
async def archive_detail(incident_id: int, request: Request, db: Session = Depends(get_db)):
    user = getattr(request.state, "user", None)
    if not user:
        return RedirectResponse("/login", status_code=302)
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(404)
    if not can_access_incident(user, incident):
        raise HTTPException(403, detail="Kein Zugriff auf diesen Einsatz")
    db.refresh(incident, ["columns", "vehicles", "tasks", "messages", "rescued_persons",
                           "breathing_troops", "log_entries"])
    return templates.TemplateResponse(request, "archive/detail.html", {
        "user": user, "incident": incident,
    })


@router.get("/archiv/{incident_id}/pdf")
async def download_pdf(incident_id: int, request: Request, db: Session = Depends(get_db)):
    user = getattr(request.state, "user", None)
    if not user:
        return RedirectResponse("/login", status_code=302)
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(404)
    if not can_access_incident(user, incident):
        raise HTTPException(403, detail="Kein Zugriff auf diesen Einsatz")
    db.refresh(incident, ["columns", "vehicles", "tasks", "messages", "rescued_persons",
                           "breathing_troops", "log_entries"])
    pdf_bytes = render_incident_pdf(incident, base_url=str(request.base_url))
    filename = f"einsatz_{incident.id}_{incident.alarm_type_code}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

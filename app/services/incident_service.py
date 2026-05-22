"""Core incident business logic – mirrors startIncident(), changeAlarm() from the HTML version."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.incident import (
    Incident, IncidentColumn, IncidentVehicle, Task, Message,
    FIXED_COLUMNS, FIXED_COLUMN_TITLES,
)
from app.models.master import AlarmType, VehicleMaster, DefaultMessage, TaskSuggestion
from app.core.audit import write_incident_change, write_audit


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_incident(
    db: Session,
    alarm_type_code: str,
    *,
    started_at: Optional[datetime] = None,
    external_key: Optional[str] = None,
    nummer: Optional[int] = None,
    is_exercise: bool = False,
    address_street: Optional[str] = None,
    address_no: Optional[str] = None,
    address_city: Optional[str] = None,
    report_text: Optional[str] = None,
    reason: Optional[str] = None,
    incident_leader_user_id: Optional[int] = None,
    api_key_id: Optional[int] = None,
    ip: Optional[str] = None,
) -> Incident:
    alarm = db.get(AlarmType, alarm_type_code)
    if alarm is None:
        alarm_type_code = "T1"

    incident = Incident(
        external_key=external_key,
        nummer=nummer,
        alarm_type_code=alarm_type_code,
        status="active",
        started_at=started_at or _now(),
        is_exercise=is_exercise,
        address_street=address_street,
        address_no=address_no,
        address_city=address_city,
        report_text=report_text,
        reason=reason,
        incident_leader_user_id=incident_leader_user_id,
    )
    db.add(incident)
    db.flush()  # get id

    _create_fixed_columns(db, incident)
    _populate_vehicles(db, incident, alarm)
    _create_default_messages(db, incident, alarm)

    write_audit(
        db, "incident.created",
        incident_id=incident.id,
        api_key_id=api_key_id,
        ip=ip,
        payload={"alarm_type_code": alarm_type_code, "is_exercise": is_exercise},
    )
    return incident


def _create_fixed_columns(db: Session, incident: Incident) -> None:
    for i, code in enumerate(FIXED_COLUMNS):
        col = IncidentColumn(
            incident_id=incident.id,
            code=code,
            title=FIXED_COLUMN_TITLES[code],
            is_fixed=True,
            display_order=i,
        )
        db.add(col)
    db.flush()


def _get_column(incident: Incident, code: str) -> Optional[IncidentColumn]:
    for col in incident.columns:
        if col.code == code:
            return col
    return None


def _populate_vehicles(db: Session, incident: Incident, alarm: Optional[AlarmType]) -> None:
    if alarm is None:
        return

    db.refresh(incident, ["columns"])
    dispatched_col = _get_column(incident, "dispatched")
    neighbor_col = _get_column(incident, "neighbor")
    if not dispatched_col:
        return

    # Own vehicles (FF Wolfurt = slug 'wolfurt')
    wolfurt_q = (
        db.query(VehicleMaster)
        .join(VehicleMaster.dept)
        .filter(VehicleMaster.active == True)  # noqa: E712
        .order_by(VehicleMaster.display_order)
    )
    from app.models.master import FireDept
    wolfurt_q = wolfurt_q.filter(FireDept.slug == "wolfurt")

    if alarm and alarm.default_first_train_only:
        wolfurt_q = wolfurt_q.filter(VehicleMaster.is_first_train == True)  # noqa: E712

    for i, vm in enumerate(wolfurt_q.all()):
        db.add(IncidentVehicle(
            incident_id=incident.id,
            column_id=dispatched_col.id,
            vehicle_master_id=vm.id,
            display_order=i,
        ))

    # Neighbor vehicles go into 'neighbor' column
    if alarm and alarm.notify_neighbors and neighbor_col:
        neighbor_q = (
            db.query(VehicleMaster)
            .join(VehicleMaster.dept)
            .filter(VehicleMaster.active == True)  # noqa: E712
            .order_by(VehicleMaster.display_order)
        )
        from app.models.master import FireDept as FD
        neighbor_q = neighbor_q.filter(FD.slug != "wolfurt")
        for i, vm in enumerate(neighbor_q.all()):
            db.add(IncidentVehicle(
                incident_id=incident.id,
                column_id=neighbor_col.id,
                vehicle_master_id=vm.id,
                display_order=i,
            ))
    db.flush()


def _create_default_messages(db: Session, incident: Incident, alarm: Optional[AlarmType]) -> None:
    if alarm is None:
        return
    msgs = db.query(DefaultMessage).filter(DefaultMessage.alarm_type_code == alarm.code).all()
    for i, dm in enumerate(msgs):
        due_at = None
        if incident.started_at and dm.due_after_sec:
            from datetime import timedelta
            started = incident.started_at if incident.started_at.tzinfo else incident.started_at.replace(tzinfo=timezone.utc)
            due_at = started + timedelta(seconds=dm.due_after_sec)
        db.add(Message(
            incident_id=incident.id,
            title=dm.text,
            due_after_sec=dm.due_after_sec,
            due_at=due_at,
            display_order=i,
        ))
    db.flush()


def add_task(
    db: Session,
    incident: Incident,
    title: str,
    detail: Optional[str] = None,
    user_id: Optional[int] = None,
) -> Task:
    tasks_col = _get_column(incident, "tasks")
    task = Task(
        incident_id=incident.id,
        column_id=tasks_col.id if tasks_col else None,
        title=title,
        detail=detail,
        created_by_user_id=user_id,
    )
    db.add(task)
    db.flush()
    write_incident_change(
        db, incident.id, "task.created", "task", task.id,
        before=None, after={"title": title, "detail": detail},
        user_id=user_id,
    )
    return task


def assign_task_to_vehicle(
    db: Session,
    task: Task,
    vehicle: IncidentVehicle,
    user_id: Optional[int] = None,
) -> Task:
    before = {"vehicle_id": task.vehicle_id, "column_id": task.column_id}
    task.vehicle_id = vehicle.id
    task.column_id = None
    db.flush()
    write_incident_change(
        db, task.incident_id, "task.assigned", "task", task.id,
        before=before, after={"vehicle_id": vehicle.id},
        user_id=user_id,
    )
    return task


def move_vehicle_to_column(
    db: Session,
    vehicle: IncidentVehicle,
    new_column: IncidentColumn,
    user_id: Optional[int] = None,
) -> IncidentVehicle:
    before = {"column_id": vehicle.column_id}
    vehicle.column_id = new_column.id
    db.flush()
    write_incident_change(
        db, vehicle.incident_id, "vehicle.moved", "incident_vehicle", vehicle.id,
        before=before, after={"column_id": new_column.id},
        user_id=user_id,
    )
    return vehicle


def close_incident(db: Session, incident: Incident, user_id: Optional[int] = None) -> Incident:
    incident.status = "closed"
    incident.closed_at = _now()
    # Revoke all QR tokens
    for token in incident.tokens:
        if token.revoked_at is None:
            token.revoked_at = _now()
    db.flush()
    write_audit(db, "incident.closed", incident_id=incident.id, user_id=user_id)
    return incident


def add_section_column(
    db: Session,
    incident: Incident,
    title: str,
    user_id: Optional[int] = None,
) -> IncidentColumn:
    max_order = max((c.display_order for c in incident.columns), default=0)
    col = IncidentColumn(
        incident_id=incident.id,
        code=f"section_{_now().timestamp():.0f}",
        title=title,
        is_fixed=False,
        display_order=max_order + 1,
    )
    db.add(col)
    db.flush()
    write_incident_change(
        db, incident.id, "column.created", "incident_column", col.id,
        before=None, after={"title": title},
        user_id=user_id,
    )
    return col

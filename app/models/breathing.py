from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

TROOP_STATUSES = ["bereit", "im_einsatz", "rueckzug", "zurueck", "erholt"]
TROOP_STATUS_LABELS = {
    "bereit":      "Bereit",
    "im_einsatz":  "Im Einsatz",
    "rueckzug":    "Rückzug!",
    "zurueck":     "Zurück",
    "erholt":      "Erholt",
}


class BreathingTroop(Base):
    __tablename__ = "breathing_troop"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    incident_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("incident.id", ondelete="CASCADE"), nullable=False)
    vehicle_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("incident_vehicle.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, default="Trupp")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="bereit")
    task_text: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    start_press_avg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    entry_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    withdraw_press_calc: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    withdraw_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    back_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    incident: Mapped["Incident"] = relationship(back_populates="breathing_troops")  # type: ignore[name-defined]
    members: Mapped[List["TroopMember"]] = relationship(
        back_populates="troop", cascade="all, delete-orphan", lazy="joined"
    )
    pressure_logs: Mapped[List["PressureLog"]] = relationship(
        back_populates="troop", order_by="PressureLog.ts", cascade="all, delete-orphan"
    )

    @property
    def elapsed_seconds(self) -> Optional[int]:
        if self.entry_at is None:
            return None
        end = self.back_at or datetime.now(timezone.utc)
        entry = self.entry_at if self.entry_at.tzinfo else self.entry_at.replace(tzinfo=timezone.utc)
        end = end if end.tzinfo else end.replace(tzinfo=timezone.utc)
        return int((end - entry).total_seconds())

    @property
    def lowest_current_pressure(self) -> Optional[float]:
        if not self.pressure_logs:
            return None
        return min(pl.pressure_bar for pl in self.pressure_logs if pl.pressure_bar is not None)


class TroopMember(Base):
    __tablename__ = "troop_member"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    troop_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("breathing_troop.id", ondelete="CASCADE"), nullable=False)
    member_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("member.id"), nullable=True)
    free_text_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    role: Mapped[str] = mapped_column(String(30), nullable=False, default="truppmann")
    start_press: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    withdraw_press: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    back_press: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    troop: Mapped["BreathingTroop"] = relationship(back_populates="members")
    member: Mapped[Optional["Member"]] = relationship(lazy="joined")  # type: ignore[name-defined]

    @property
    def display_name(self) -> str:
        if self.member:
            return self.member.full_name
        return self.free_text_name or "Unbekannt"


class PressureLog(Base):
    __tablename__ = "pressure_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    troop_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("breathing_troop.id", ondelete="CASCADE"), nullable=False)
    ts: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    member_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("member.id"), nullable=True)
    pressure_bar: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_by_user_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=True)

    troop: Mapped["BreathingTroop"] = relationship(back_populates="pressure_logs")


# Forward reference resolution
from app.models.incident import Incident  # noqa: E402, F401

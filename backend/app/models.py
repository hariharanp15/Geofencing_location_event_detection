import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class BoundaryType(str, enum.Enum):
    circle = "circle"
    polygon = "polygon"


class EventType(str, enum.Enum):
    enter = "enter"
    exit = "exit"
    inside = "inside"
    outside = "outside"


class FenceState(str, enum.Enum):
    inside = "inside"
    outside = "outside"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)


class Device(TimestampMixin, Base):
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    label: Mapped[str] = mapped_column(String(120))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User | None] = relationship()


class Geofence(TimestampMixin, Base):
    __tablename__ = "geofences"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True)
    boundary_type: Mapped[BoundaryType] = mapped_column(Enum(BoundaryType))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    center_latitude: Mapped[float | None] = mapped_column(Float)
    center_longitude: Mapped[float | None] = mapped_column(Float)
    radius_meters: Mapped[float | None] = mapped_column(Float)
    accuracy_buffer_meters: Mapped[float] = mapped_column(Float, default=15)
    tracking_interval_seconds: Mapped[int] = mapped_column(Integer, default=60)
    event_rules: Mapped[dict] = mapped_column(JSON, default=lambda: {"enter": True, "exit": True, "inside": True, "outside": True})
    points: Mapped[list["GeofencePoint"]] = relationship(cascade="all, delete-orphan", order_by="GeofencePoint.position")


class GeofencePoint(Base):
    __tablename__ = "geofence_points"
    id: Mapped[int] = mapped_column(primary_key=True)
    geofence_id: Mapped[int] = mapped_column(ForeignKey("geofences.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)


class LocationEvent(Base):
    __tablename__ = "location_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class GeofenceEvent(Base):
    __tablename__ = "geofence_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), index=True)
    geofence_id: Mapped[int] = mapped_column(ForeignKey("geofences.id"), index=True)
    # One submitted location can legitimately produce events for several fences.
    location_event_id: Mapped[int] = mapped_column(ForeignKey("location_events.id"), index=True)
    event_type: Mapped[EventType] = mapped_column(Enum(EventType), index=True)
    previous_state: Mapped[FenceState | None] = mapped_column(Enum(FenceState), nullable=True)
    current_state: Mapped[FenceState] = mapped_column(Enum(FenceState))
    occurred_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    geofence: Mapped[Geofence] = relationship()
    device: Mapped[Device] = relationship()


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[str] = mapped_column(String(80))
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[str] = mapped_column(String(80))
    details: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class PointIn(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    model_config = {"from_attributes": True}


class GeofenceBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    boundary_type: Literal["circle", "polygon"]
    enabled: bool = True
    center_latitude: float | None = Field(default=None, ge=-90, le=90)
    center_longitude: float | None = Field(default=None, ge=-180, le=180)
    radius_meters: float | None = Field(default=None, gt=0, le=100000)
    accuracy_buffer_meters: float = Field(default=15, ge=0, le=500)
    tracking_interval_seconds: int = Field(default=60, ge=1, le=86_400)
    event_rules: dict[str, bool] = Field(default_factory=lambda: {"enter": True, "exit": True, "inside": True, "outside": True})
    points: list[PointIn] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_boundary(self):
        if self.boundary_type == "circle" and None in (self.center_latitude, self.center_longitude, self.radius_meters):
            raise ValueError("Circle fences require center latitude, longitude, and radius")
        if self.boundary_type == "polygon" and len(self.points) < 3:
            raise ValueError("Polygon fences require at least three points")
        return self


class GeofenceCreate(GeofenceBase):
    pass


class GeofenceUpdate(GeofenceBase):
    pass


class GeofencePatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    enabled: bool | None = None
    accuracy_buffer_meters: float | None = Field(default=None, ge=0, le=500)
    tracking_interval_seconds: int | None = Field(default=None, ge=1, le=86_400)
    event_rules: dict[str, bool] | None = None


class GeofenceOut(GeofenceBase):
    id: int
    model_config = {"from_attributes": True}


class DeviceCreate(BaseModel):
    external_id: str = Field(min_length=1, max_length=120)
    label: str = Field(min_length=1, max_length=120)
    user_id: int | None = None
    enabled: bool = True
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class DeviceOut(DeviceCreate):
    id: int
    model_config = {"from_attributes": True}


class DeviceUpdate(DeviceCreate):
    pass


class DevicePatch(BaseModel):
    external_id: str | None = Field(default=None, min_length=1, max_length=120)
    label: str | None = Field(default=None, min_length=1, max_length=120)
    user_id: int | None = None
    enabled: bool | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class LocationIn(PointIn):
    device_external_id: str = Field(min_length=1, max_length=120)
    timestamp: datetime


class DetectedEvent(BaseModel):
    geofence_id: int
    geofence_name: str
    event_type: str
    previous_state: str | None
    current_state: str


class LocationResult(BaseModel):
    location_event_id: int
    events: list[DetectedEvent]


class LocationOut(BaseModel):
    id: int
    device_id: int
    latitude: float
    longitude: float
    recorded_at: datetime
    received_at: datetime
    model_config = {"from_attributes": True}


class GeofenceEventOut(BaseModel):
    id: int
    event_type: str
    previous_state: str | None
    current_state: str
    occurred_at: datetime
    latitude: float
    longitude: float
    geofence_id: int
    geofence_name: str
    device_name: str
    device_external_id: str


class EventSummary(BaseModel):
    total: int
    enter: int
    exit: int
    inside: int
    outside: int


class AuditLogOut(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: str
    details: str | None
    created_at: datetime
    model_config = {"from_attributes": True}

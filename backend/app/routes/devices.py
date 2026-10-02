from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AuditLog, Device, GeofenceEvent
from ..schemas import DeviceCreate, DeviceOut, DevicePatch, DeviceUpdate, GeofenceEventOut
from ..services.detection import record_location_and_events

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("", response_model=list[DeviceOut])
def list_devices(db: Session = Depends(get_db)):
    return db.scalars(select(Device).order_by(Device.label)).all()


@router.post("", response_model=DeviceOut, status_code=status.HTTP_201_CREATED)
def create_device(data: DeviceCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Device).where(Device.external_id == data.external_id)):
        raise HTTPException(409, "A device with this external ID already exists")
    device = Device(**data.model_dump())
    db.add(device); db.flush()
    if device.enabled and device.latitude is not None and device.longitude is not None:
        record_location_and_events(db, device, device.latitude, device.longitude, datetime.utcnow())
    db.add(AuditLog(action="created", entity_type="device", entity_id=str(device.id), details=device.label))
    db.commit(); db.refresh(device)
    return device


def get_device(db: Session, device_id: int) -> Device:
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(404, "Device not found")
    return device


@router.put("/{device_id}", response_model=DeviceOut)
def update_device(device_id: int, data: DeviceUpdate, db: Session = Depends(get_db)):
    device = get_device(db, device_id)
    duplicate = db.scalar(select(Device).where(Device.external_id == data.external_id, Device.id != device_id))
    if duplicate:
        raise HTTPException(409, "A device with this external ID already exists")
    for key, value in data.model_dump().items():
        setattr(device, key, value)
    if device.enabled and device.latitude is not None and device.longitude is not None:
        record_location_and_events(db, device, device.latitude, device.longitude, datetime.utcnow())
    db.add(AuditLog(action="updated", entity_type="device", entity_id=str(device.id), details=device.label))
    db.commit(); db.refresh(device)
    return device


@router.get("/{device_id}", response_model=DeviceOut)
def read_device(device_id: int, db: Session = Depends(get_db)):
    return get_device(db, device_id)


@router.patch("/{device_id}", response_model=DeviceOut)
def patch_device(device_id: int, data: DevicePatch, db: Session = Depends(get_db)):
    device = get_device(db, device_id)
    values = data.model_dump(exclude_none=True)
    if "external_id" in values:
        duplicate = db.scalar(select(Device).where(Device.external_id == values["external_id"], Device.id != device_id))
        if duplicate:
            raise HTTPException(409, "A device with this external ID already exists")
    for key, value in values.items():
        setattr(device, key, value)
    if device.enabled and device.latitude is not None and device.longitude is not None and {"latitude", "longitude"}.intersection(values):
        record_location_and_events(db, device, device.latitude, device.longitude, datetime.utcnow())
    db.add(AuditLog(action="patched", entity_type="device", entity_id=str(device.id), details=device.label))
    db.commit(); db.refresh(device)
    return device


@router.patch("/{device_id}/status", response_model=DeviceOut)
def set_device_status(device_id: int, enabled: bool, db: Session = Depends(get_db)):
    device = get_device(db, device_id)
    device.enabled = enabled
    db.add(AuditLog(action="status_changed", entity_type="device", entity_id=str(device.id), details=str(enabled)))
    db.commit(); db.refresh(device)
    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(device_id: int, db: Session = Depends(get_db)):
    device = get_device(db, device_id)
    db.add(AuditLog(action="deleted", entity_type="device", entity_id=str(device.id), details=device.label))
    db.delete(device)
    db.commit()


@router.get("/{device_id}/events", response_model=list[GeofenceEventOut])
def device_events(device_id: int, limit: int = 100, db: Session = Depends(get_db)):
    device = get_device(db, device_id)
    events = db.scalars(select(GeofenceEvent).where(GeofenceEvent.device_id == device.id).order_by(GeofenceEvent.occurred_at.desc()).limit(min(max(limit, 1), 1_000))).all()
    return [GeofenceEventOut(id=e.id, event_type=e.event_type.value, previous_state=e.previous_state.value if e.previous_state else None, current_state=e.current_state.value, occurred_at=e.occurred_at, latitude=e.latitude, longitude=e.longitude, geofence_id=e.geofence_id, geofence_name=e.geofence.name, device_name=device.label, device_external_id=device.external_id) for e in events]

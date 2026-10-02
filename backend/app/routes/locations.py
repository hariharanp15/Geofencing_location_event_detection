from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Device, LocationEvent
from ..schemas import DetectedEvent, LocationIn, LocationOut, LocationResult
from ..services.detection import record_location_and_events

router = APIRouter(prefix="/locations", tags=["location tracking"])


@router.get("/{device_id}/latest", response_model=LocationOut)
def latest_location(device_id: int, db: Session = Depends(get_db)):
    if not db.get(Device, device_id):
        raise HTTPException(404, "Device not found")
    location = db.scalar(select(LocationEvent).where(LocationEvent.device_id == device_id).order_by(desc(LocationEvent.recorded_at), desc(LocationEvent.id)).limit(1))
    if not location:
        raise HTTPException(404, "No location has been recorded for this device")
    return location


@router.get("/{device_id}/history", response_model=list[LocationOut])
def location_history(device_id: int, limit: int = 100, db: Session = Depends(get_db)):
    if not db.get(Device, device_id):
        raise HTTPException(404, "Device not found")
    return db.scalars(select(LocationEvent).where(LocationEvent.device_id == device_id).order_by(desc(LocationEvent.recorded_at), desc(LocationEvent.id)).limit(min(max(limit, 1), 1_000))).all()


@router.post("", response_model=LocationResult, status_code=status.HTTP_201_CREATED)
def ingest_location(data: LocationIn, db: Session = Depends(get_db)):
    device = db.scalar(select(Device).where(Device.external_id == data.device_external_id))
    if not device:
        raise HTTPException(404, "Device not found; register it before sending locations")
    if not device.enabled:
        raise HTTPException(409, "Device is inactive")
    device.latitude = data.latitude
    device.longitude = data.longitude
    location_id, created = record_location_and_events(db, device, data.latitude, data.longitude, data.timestamp)
    db.commit()
    return LocationResult(location_event_id=location_id, events=[DetectedEvent(
        geofence_id=fence.id, geofence_name=fence.name, event_type=event.event_type.value,
        previous_state=event.previous_state.value if event.previous_state else None, current_state=event.current_state.value
    ) for fence, event in created])

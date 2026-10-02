from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import EventType, GeofenceEvent
from ..schemas import EventSummary, GeofenceEventOut

router = APIRouter(prefix="/events", tags=["event history"])


@router.get("", response_model=list[GeofenceEventOut])
def list_events(limit: int | None = None, device_external_id: str | None = None, geofence_id: int | None = None, event_type: EventType | None = None, from_time: datetime | None = None, to_time: datetime | None = None, db: Session = Depends(get_db)):
    query = select(GeofenceEvent).options(joinedload(GeofenceEvent.geofence), joinedload(GeofenceEvent.device))
    if device_external_id:
        query = query.where(GeofenceEvent.device.has(external_id=device_external_id))
    if geofence_id:
        query = query.where(GeofenceEvent.geofence_id == geofence_id)
    if event_type:
        query = query.where(GeofenceEvent.event_type == event_type)
    if from_time:
        query = query.where(GeofenceEvent.occurred_at >= from_time)
    if to_time:
        query = query.where(GeofenceEvent.occurred_at <= to_time)
    if limit is not None:
        query = query.limit(min(max(limit, 1), 1_000))
    records = db.scalars(query.order_by(desc(GeofenceEvent.occurred_at))).all()
    return [GeofenceEventOut(id=e.id, event_type=e.event_type.value, previous_state=e.previous_state.value if e.previous_state else None,
        current_state=e.current_state.value, occurred_at=e.occurred_at, latitude=e.latitude, longitude=e.longitude,
        geofence_id=e.geofence_id, geofence_name=e.geofence.name, device_name=e.device.label, device_external_id=e.device.external_id) for e in records]


@router.get("/summary", response_model=EventSummary)
def event_summary(db: Session = Depends(get_db)):
    values = dict(db.execute(select(GeofenceEvent.event_type, func.count(GeofenceEvent.id)).group_by(GeofenceEvent.event_type)).all())
    return EventSummary(total=sum(values.values()), enter=values.get(EventType.enter, 0), exit=values.get(EventType.exit, 0), inside=values.get(EventType.inside, 0), outside=values.get(EventType.outside, 0))


@router.get("/{event_id}", response_model=GeofenceEventOut)
def read_event(event_id: int, db: Session = Depends(get_db)):
    event = db.scalar(select(GeofenceEvent).options(joinedload(GeofenceEvent.geofence), joinedload(GeofenceEvent.device)).where(GeofenceEvent.id == event_id))
    if not event:
        from fastapi import HTTPException
        raise HTTPException(404, "Event not found")
    return GeofenceEventOut(id=event.id, event_type=event.event_type.value, previous_state=event.previous_state.value if event.previous_state else None, current_state=event.current_state.value, occurred_at=event.occurred_at, latitude=event.latitude, longitude=event.longitude, geofence_id=event.geofence_id, geofence_name=event.geofence.name, device_name=event.device.label, device_external_id=event.device.external_id)

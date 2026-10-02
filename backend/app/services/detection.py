from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..models import Device, EventType, FenceState, Geofence, GeofenceEvent, LocationEvent
from .geometry import distance_meters, point_in_polygon


def fence_contains(fence: Geofence, latitude: float, longitude: float, previous: FenceState | None) -> bool:
    if fence.boundary_type.value == "circle":
        distance = distance_meters(latitude, longitude, fence.center_latitude, fence.center_longitude)
        # Hysteresis: retain the prior state within the accuracy band.
        threshold = fence.radius_meters + (fence.accuracy_buffer_meters if previous == FenceState.inside else -fence.accuracy_buffer_meters)
        return distance <= threshold
    return point_in_polygon(latitude, longitude, [(p.latitude, p.longitude) for p in fence.points])


def latest_event(db: Session, device_id: int, geofence_id: int) -> GeofenceEvent | None:
    return db.scalar(select(GeofenceEvent).where(
        GeofenceEvent.device_id == device_id, GeofenceEvent.geofence_id == geofence_id
    ).order_by(desc(GeofenceEvent.occurred_at), desc(GeofenceEvent.id)).limit(1))


def classify(previous: FenceState | None, current: FenceState) -> EventType:
    if previous is None:
        return EventType.inside if current == FenceState.inside else EventType.outside
    if previous == FenceState.outside and current == FenceState.inside:
        return EventType.enter
    if previous == FenceState.inside and current == FenceState.outside:
        return EventType.exit
    return EventType.inside if current == FenceState.inside else EventType.outside


def record_location_and_events(db: Session, device: Device, latitude: float, longitude: float, timestamp: datetime) -> tuple[int, list[tuple[Geofence, GeofenceEvent]]]:
    """Persist a raw location and interval-controlled geofence history without replacing prior events."""
    location = LocationEvent(device_id=device.id, latitude=latitude, longitude=longitude, recorded_at=timestamp)
    db.add(location)
    db.flush()
    created: list[tuple[Geofence, GeofenceEvent]] = []
    fences = db.scalars(select(Geofence).where(Geofence.enabled.is_(True))).all()
    for fence in fences:
        # Relationship loading is explicit because this service is also used outside HTTP requests.
        db.refresh(fence, attribute_names=["points"])
        previous_event = latest_event(db, device.id, fence.id)
        previous = previous_event.current_state if previous_event else None
        current = FenceState.inside if fence_contains(fence, latitude, longitude, previous) else FenceState.outside
        event_type = classify(previous, current)
        state_changed = previous is None or previous != current
        interval_elapsed = previous_event is None or (timestamp - previous_event.occurred_at).total_seconds() >= fence.tracking_interval_seconds
        if not state_changed and not interval_elapsed:
            continue
        if not fence.event_rules.get(event_type.value, True):
            continue
        event = GeofenceEvent(device_id=device.id, geofence_id=fence.id, location_event_id=location.id, event_type=event_type,
                              previous_state=previous, current_state=current, occurred_at=timestamp, latitude=latitude, longitude=longitude)
        db.add(event)
        created.append((fence, event))
    return location.id, created

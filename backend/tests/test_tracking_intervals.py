from datetime import datetime, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Device, EventType, Geofence, GeofenceEvent, BoundaryType
from app.services.detection import record_location_and_events


def test_records_transitions_immediately_and_unchanged_state_on_interval():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        device = Device(external_id="tracker-1", label="Tracker")
        fence = Geofence(name="Office", boundary_type=BoundaryType.circle, center_latitude=0, center_longitude=0,
                         radius_meters=100, tracking_interval_seconds=60, event_rules={"enter": True, "exit": True, "inside": True, "outside": True})
        db.add_all([device, fence]); db.commit()
        start = datetime(2026, 1, 1, 9, 0, 0)

        record_location_and_events(db, device, 0, 0, start)                         # initial INSIDE
        record_location_and_events(db, device, 0, 0, start + timedelta(seconds=10)) # suppressed
        record_location_and_events(db, device, 0, 0, start + timedelta(seconds=60)) # interval INSIDE
        record_location_and_events(db, device, 1, 1, start + timedelta(seconds=61)) # EXIT immediately
        db.commit()

        types = db.scalars(select(GeofenceEvent.event_type).order_by(GeofenceEvent.occurred_at)).all()
        assert types == [EventType.inside, EventType.inside, EventType.exit]

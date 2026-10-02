from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import AuditLog, Geofence, GeofencePoint
from ..schemas import GeofenceCreate, GeofenceOut, GeofencePatch, GeofenceUpdate

router = APIRouter(prefix="/geofences", tags=["geofences"])


def get_fence(db: Session, fence_id: int) -> Geofence:
    fence = db.scalar(select(Geofence).options(selectinload(Geofence.points)).where(Geofence.id == fence_id))
    if not fence:
        raise HTTPException(404, "Geofence not found")
    return fence


def apply_fence(fence: Geofence, data: GeofenceCreate | GeofenceUpdate):
    values = data.model_dump(exclude={"points"})
    for key, value in values.items():
        setattr(fence, key, value)
    fence.points = [GeofencePoint(position=i, latitude=p.latitude, longitude=p.longitude) for i, p in enumerate(data.points)]


@router.get("", response_model=list[GeofenceOut])
def list_geofences(db: Session = Depends(get_db)):
    return db.scalars(select(Geofence).options(selectinload(Geofence.points)).order_by(Geofence.name)).all()


@router.post("", response_model=GeofenceOut, status_code=status.HTTP_201_CREATED)
def create_geofence(data: GeofenceCreate, db: Session = Depends(get_db)):
    fence = Geofence()
    apply_fence(fence, data)
    db.add(fence)
    db.flush()
    db.add(AuditLog(action="created", entity_type="geofence", entity_id=str(fence.id), details=fence.name))
    db.commit(); db.refresh(fence)
    return get_fence(db, fence.id)


@router.get("/{fence_id}", response_model=GeofenceOut)
def read_geofence(fence_id: int, db: Session = Depends(get_db)):
    return get_fence(db, fence_id)


@router.put("/{fence_id}", response_model=GeofenceOut)
def update_geofence(fence_id: int, data: GeofenceUpdate, db: Session = Depends(get_db)):
    fence = get_fence(db, fence_id)
    apply_fence(fence, data)
    db.add(AuditLog(action="updated", entity_type="geofence", entity_id=str(fence.id), details=fence.name))
    db.commit()
    return get_fence(db, fence_id)


@router.patch("/{fence_id}", response_model=GeofenceOut)
def patch_geofence(fence_id: int, data: GeofencePatch, db: Session = Depends(get_db)):
    fence = get_fence(db, fence_id)
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(fence, key, value)
    db.add(AuditLog(action="patched", entity_type="geofence", entity_id=str(fence.id), details=fence.name))
    db.commit()
    return get_fence(db, fence_id)


@router.patch("/{fence_id}/status", response_model=GeofenceOut)
def set_geofence_status(fence_id: int, enabled: bool, db: Session = Depends(get_db)):
    fence = get_fence(db, fence_id)
    fence.enabled = enabled
    db.add(AuditLog(action="toggled", entity_type="geofence", entity_id=str(fence.id), details=str(fence.enabled)))
    db.commit()
    return get_fence(db, fence_id)


@router.delete("/{fence_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_geofence(fence_id: int, db: Session = Depends(get_db)):
    fence = get_fence(db, fence_id)
    db.add(AuditLog(action="deleted", entity_type="geofence", entity_id=str(fence.id), details=fence.name))
    db.delete(fence)
    db.commit()

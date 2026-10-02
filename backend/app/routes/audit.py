from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AuditLog
from ..schemas import AuditLogOut

router = APIRouter(prefix="/audit-logs", tags=["audit logs"])


@router.get("", response_model=list[AuditLogOut])
def list_audit_logs(entity_type: str | None = None, limit: int = 100, db: Session = Depends(get_db)):
    query = select(AuditLog)
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    return db.scalars(query.order_by(desc(AuditLog.created_at)).limit(min(max(limit, 1), 1_000))).all()

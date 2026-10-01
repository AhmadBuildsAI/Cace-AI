from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ...core.database import get_db
from ...models.user import User
from ...models.security_event import SecurityEvent
from ...schemas.security import SecurityEventItem, SecurityDashboard
from ...api.dependencies.auth import get_current_user

router = APIRouter(prefix="/security", tags=["security"])


@router.get("/dashboard", response_model=SecurityDashboard)
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    events = db.query(SecurityEvent).order_by(desc(SecurityEvent.created_at)).all()
    threat_types = {}
    for e in events:
        threat_types[e.threat_type] = threat_types.get(e.threat_type, 0) + 1
    
    recent = events[:10]
    return SecurityDashboard(
        total_events=len(events),
        blocked_count=sum(1 for e in events if e.blocked == "true"),
        threat_distribution=[{"threat_type": k, "count": v} for k, v in threat_types.items()],
        recent_events=[
            SecurityEventItem(
                id=str(e.id),
                threat_type=e.threat_type,
                severity=e.severity,
                confidence=e.confidence,
                reasoning=e.reasoning,
                blocked=e.blocked,
                created_at=e.created_at.isoformat(),
            ) for e in recent
        ],
    )

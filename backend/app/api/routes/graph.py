from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models.user import User
from ...schemas.graph import GraphResponse
from ...services.graph_service import get_full_graph, traverse_context
from ...api.dependencies.auth import get_current_user

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/", response_model=GraphResponse)
def full_graph(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_full_graph(db, current_user.role)


@router.get("/traverse")
def traverse(
    node_id: str,
    depth: int = Query(2, ge=1, le=5),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return traverse_context(db, node_id, depth, current_user.role)

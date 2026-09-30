import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..auth import current_user
from ..database import get_db
from ..models.db_models import RecommendationHistory, User
from ..models.schemas import HistoryItem, UserOut

router = APIRouter(tags=["session"])

@router.get("/session-info", response_model=UserOut)
def session_info(user: User = Depends(current_user)): return user

@router.get("/session-data")
def session_data(user: User = Depends(current_user), db: Session = Depends(get_db)):
    count = db.query(RecommendationHistory).filter_by(user_id=user.id).count()
    return {"user_id": user.id, "email": user.email, "recommendation_count": count}

@router.get("/history", response_model=list[HistoryItem])
def history(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(RecommendationHistory).filter_by(user_id=user.id).order_by(RecommendationHistory.created_at.desc()).limit(50).all()
    return [HistoryItem(id=r.id, planner=r.planner, created_at=r.created_at.isoformat(), request=json.loads(r.request_json), response=json.loads(r.response_json)) for r in rows]

@router.get("/recommendations-details/{history_id}")
def recommendation_details(history_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = db.query(RecommendationHistory).filter_by(id=history_id, user_id=user.id).first()
    if not row: return {"detail": "Recommendation not found"}
    return {"id": row.id, "planner": row.planner, "request": json.loads(row.request_json), "response": json.loads(row.response_json), "created_at": row.created_at.isoformat()}

import json
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from ..auth import current_user
from ..database import get_db
from ..models.db_models import RecommendationHistory, User
from ..models.schemas import HomeRequest, PartyRequest, JewelryRequest, RecommendationResponse
from ..services.recommendation import generate

router = APIRouter(tags=["planners"])

def save_history(db: Session, user: User, planner: str, request_data: dict, result: RecommendationResponse):
    db.add(RecommendationHistory(user_id=user.id, planner=planner, request_json=json.dumps(request_data, ensure_ascii=False), response_json=result.model_dump_json()))
    db.commit()

@router.post("/generate-home", response_model=RecommendationResponse)
async def generate_home(payload: HomeRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    result = await generate("home", payload.model_dump())
    save_history(db, user, "home", payload.model_dump(), result); return result

@router.post("/generate-party", response_model=RecommendationResponse)
async def generate_party(payload: PartyRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    result = await generate("party", payload.model_dump())
    save_history(db, user, "party", payload.model_dump(), result); return result

@router.post("/generate-jewelry", response_model=RecommendationResponse)
async def generate_jewelry(budget: float = Form(...), occasion: str = Form(...), style: str = Form("elegant"), outfit_color: str = Form("not specified"), metal: str = Form("any"), preferences: str = Form("comfortable and versatile"), outfit_image: UploadFile | None = File(None), user: User = Depends(current_user), db: Session = Depends(get_db)):
    payload = JewelryRequest(budget=budget, occasion=occasion, style=style, outfit_color=outfit_color, metal=metal, preferences=preferences)
    image_bytes = await outfit_image.read() if outfit_image else None
    if image_bytes and len(image_bytes) > 5 * 1024 * 1024:
        raise HTTPException(413, "Image must be 5 MB or smaller")
    if outfit_image and outfit_image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(400, "Use JPG, PNG, or WEBP image")
    result = await generate("jewelry", payload.model_dump(), image_bytes, outfit_image.content_type if outfit_image else None)
    save_history(db, user, "jewelry", payload.model_dump(), result); return result

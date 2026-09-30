from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class HomeItem(BaseModel):
    room: str
    category: str
    item: str
    quantity: int = Field(ge=1, le=50)

class HomeRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    style: str = Field(default="Modern", max_length=80)
    rooms: list[HomeItem] = Field(min_length=1, max_length=50)
    priorities: str = Field(default="value for money", max_length=300)

class PartyRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    guests: int = Field(gt=0, le=10_000)
    event_type: str = Field(min_length=2, max_length=80)
    venue: str = Field(default="flexible", max_length=120)
    city: str = Field(default="Chennai", max_length=120)
    preferences: str = Field(default="balanced", max_length=500)

class JewelryRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    occasion: str = Field(min_length=2, max_length=80)
    style: str = Field(default="elegant", max_length=80)
    outfit_color: str = Field(default="not specified", max_length=80)
    metal: str = Field(default="any", max_length=80)
    preferences: str = Field(default="comfortable and versatile", max_length=500)

class Recommendation(BaseModel):
    name: str
    category: str
    platform: str
    estimated_price: float = Field(ge=0)
    quantity: int = Field(default=1, ge=1)
    reason: str
    search_url: str
    priority: Literal["essential", "recommended", "optional"] = "recommended"

class BudgetAllocation(BaseModel):
    category: str
    amount: float = Field(ge=0)
    percentage: float = Field(ge=0, le=100)
    note: str

class RecommendationResponse(BaseModel):
    planner: Literal["home", "party", "jewelry"]
    summary: str
    budget: float
    estimated_total: float
    remaining_budget: float
    allocations: list[BudgetAllocation]
    recommendations: list[Recommendation]
    tips: list[str]
    ai_powered: bool
    image_insight: str | None = None

class HistoryItem(BaseModel):
    id: int
    planner: str
    created_at: str
    request: dict[str, Any]
    response: dict[str, Any]

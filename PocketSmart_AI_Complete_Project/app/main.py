from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .config import get_settings
from .database import Base, engine
from .routers import auth, planners, session
from .models import db_models

BASE = Path(__file__).resolve().parent
settings = get_settings()
Base.metadata.create_all(bind=engine)
app = FastAPI(title=settings.app_name, version="1.0.0", description="Budget-aware AI recommendation assistant")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")
app.include_router(auth.router)
app.include_router(planners.router)
app.include_router(session.router)

@app.get("/api/health")
def health(): return {"status": "ok", "ai_configured": bool(settings.gemini_api_key), "model": settings.gemini_model}

@app.get("/", response_class=HTMLResponse)
def index(request: Request): return templates.TemplateResponse("index.html", {"request": request})

@app.get("/{page}", response_class=HTMLResponse)
def pages(request: Request, page: str):
    allowed = {"login": "login.html", "register": "register.html", "dashboard": "dashboard.html", "home-planner": "home_planner.html", "party-planner": "party_planner.html", "jewelry-planner": "jewelry_planner.html", "history": "history.html"}
    if page not in allowed: return RedirectResponse("/")
    return templates.TemplateResponse(allowed[page], {"request": request})

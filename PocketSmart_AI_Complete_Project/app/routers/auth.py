from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from ..auth import create_access_token, hash_password, verify_password
from ..database import get_db
from ..models.db_models import User
from ..models.schemas import LoginRequest, RegisterRequest, TokenOut, UserOut

router = APIRouter(tags=["auth"])

@router.post("/register", response_model=TokenOut, status_code=201)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "Email already registered")
    user = User(name=payload.name.strip(), email=email, password_hash=hash_password(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    token = create_access_token(user); response.set_cookie("access_token", token, httponly=True, samesite="lax", max_age=86400)
    return TokenOut(access_token=token, user=user)

@router.post("/login", response_model=TokenOut)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    token = create_access_token(user); response.set_cookie("access_token", token, httponly=True, samesite="lax", max_age=86400)
    return TokenOut(access_token=token, user=user)

@router.post("/token", response_model=TokenOut)
def token(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    access = create_access_token(user)
    response.set_cookie("access_token", access, httponly=True, samesite="lax", max_age=86400)
    return TokenOut(access_token=access, user=user)

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}

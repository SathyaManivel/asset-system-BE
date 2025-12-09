from fastapi import APIRouter, Depends, HTTPException
from ..deps import get_db, create_access_token, decode_token, verify_password
from .. import crud, schemas
from fastapi import status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/auth")

@router.post("/register", response_model=dict)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="User exists")
    u = crud.create_user(db, user.username, user.password, user.full_name, user.base_id)
    return {"id": u.id, "username": u.username}

@router.post("/token", response_model=schemas.Token)
def login(form_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    token = create_access_token({"sub": user.id, "username": user.username, "base_id": user.base_id})
    return {"access_token": token, "token_type":"bearer"}

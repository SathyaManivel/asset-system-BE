from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db, decode_token, oauth2_scheme
from .. import crud, schemas
from fastapi import HTTPException

router = APIRouter(prefix="/api/assets")

@router.get("/")
def list_assets(db: Session = Depends(get_db)):
    return db.query(crud.__import__("..models", fromlist=["models"]).models.Asset).all()

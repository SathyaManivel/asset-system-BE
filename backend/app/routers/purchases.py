from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db, oauth2_scheme, decode_token
from .. import crud, schemas
from fastapi import HTTPException

router = APIRouter(prefix="/api/purchases")

@router.post("/")
def create_purchase(purchase: schemas.PurchaseCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # decode token quickly (demo)
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401)
    user_id = payload.get("sub")
    items = [{"asset_id": it.asset_id, "quantity": it.quantity} for it in purchase.items]
    crud.add_purchase(db, purchase.base_id, items, user_id)
    return {"ok": True}

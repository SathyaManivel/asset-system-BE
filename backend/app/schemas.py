from pydantic import BaseModel
from typing import Optional, List

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    base_id: Optional[int] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AssetIn(BaseModel):
    sku: str
    name: str
    category: str
    unit: str

class PurchaseItem(BaseModel):
    asset_id: int
    quantity: int

class PurchaseCreate(BaseModel):
    base_id: int
    items: List[PurchaseItem]

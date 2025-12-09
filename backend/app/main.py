# backend/app/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

app = FastAPI(title="Military Asset Management System")

# CORS Configuration
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# ==================== In-Memory Database ====================
users_db = {
	"admin1": {"password": "admin123", "role": "admin", "base_id": None, "name": "Admin User"},
	"commander1": {"password": "cmd123", "role": "base_commander", "base_id": 1, "name": "Base 1 Commander"},
	"commander2": {"password": "cmd123", "role": "base_commander", "base_id": 2, "name": "Base 2 Commander"},
	"logistics1": {"password": "log123", "role": "logistics_officer", "base_id": 1, "name": "Logistics Officer"},
}

bases_db = [
	{"id": 1, "name": "Base Alpha"},
	{"id": 2, "name": "Base Bravo"},
	{"id": 3, "name": "Base Charlie"},
]

equipment_db = [
	{"id": 1, "name": "Rifle M4", "category": "Weapon", "unit": "piece"},
	{"id": 2, "name": "Ammunition 5.56mm", "category": "Ammo", "unit": "box"},
	{"id": 3, "name": "Military Vehicle", "category": "Transport", "unit": "vehicle"},
	{"id": 4, "name": "Helmet", "category": "Protective Gear", "unit": "piece"},
]

# In-memory storage for transactions
stock_data = {}
purchases_db = []
transfers_db = []
assignments_db = []
expended_db = []

# ==================== Pydantic Models ====================
class LoginRequest(BaseModel):
	username: str
	password: str

class LoginResponse(BaseModel):
	access_token: str
	token_type: str
	user: dict

class PurchaseCreate(BaseModel):
	base_id: int
	equipment_id: int
	quantity: int
	purchase_date: Optional[str] = None

class TransferCreate(BaseModel):
	from_base_id: int
	to_base_id: int
	equipment_id: int
	quantity: int
	transfer_date: Optional[str] = None

class AssignmentCreate(BaseModel):
	base_id: int
	equipment_id: int
	personnel_name: str
	quantity: int
	assigned_date: Optional[str] = None

class ExpenditureCreate(BaseModel):
	base_id: int
	equipment_id: int
	quantity: int
	expended_date: Optional[str] = None

# ==================== Helper Functions ====================
def verify_token(token: str):
	"""Decode and verify JWT token (simplified)"""
	if not token:
		raise HTTPException(status_code=401, detail="Invalid token")
	
	# Handle both old and new token formats
	username = None
	if token.startswith("demo-token-"):
		username = token.replace("demo-token-", "")
	else:
		username = token.replace("demo-token-", "")
	
	if username not in users_db:
		raise HTTPException(status_code=401, detail="User not found")
	return users_db[username]

def check_rbac(user: dict, required_role: str = None, base_id: int = None):
	"""Check role-based access control"""
	if required_role and user["role"] != "admin" and user["role"] != required_role:
		raise HTTPException(status_code=403, detail="Access denied")
	if base_id and user["role"] == "base_commander" and user["base_id"] != base_id:
		raise HTTPException(status_code=403, detail="Access denied for this base")

def initialize_stock():
	"""Initialize stock for bases"""
	for base in bases_db:
		if base["id"] not in stock_data:
			stock_data[base["id"]] = {}
			for eq in equipment_db:
				stock_data[base["id"]][eq["id"]] = {"opening": 100, "current": 100}

initialize_stock()

# ==================== Authentication ====================
@app.post("/api/auth/token", response_model=LoginResponse)
def login(form_data: LoginRequest):
	"""User login with role-based access"""
	if form_data.username not in users_db:
		raise HTTPException(status_code=400, detail="Invalid credentials")
	
	user = users_db[form_data.username]
	if user["password"] != form_data.password:
		raise HTTPException(status_code=400, detail="Invalid credentials")
	
	token = f"demo-token-{form_data.username}"
	return {
		"access_token": token,
		"token_type": "bearer",
		"user": {
			"username": form_data.username,
			"role": user["role"],
			"base_id": user["base_id"],
			"name": user["name"],
		}
	}

# ==================== Dashboard ====================
@app.get("/api/dashboard")
def get_dashboard(
	base_id: int = 1,
	start_date: Optional[str] = None,
	end_date: Optional[str] = None,
	token: str = None
):
	"""Get dashboard metrics for a base"""
	if token:
		user = verify_token(token)
		check_rbac(user, base_id=base_id)
	
	# Calculate metrics
	opening = sum(stock["opening"] for stock in stock_data.get(base_id, {}).values())
	
	purchases = sum(p["quantity"] for p in purchases_db if p["base_id"] == base_id)
	transfer_in = sum(t["quantity"] for t in transfers_db if t["to_base_id"] == base_id)
	transfer_out = sum(t["quantity"] for t in transfers_db if t["from_base_id"] == base_id)
	assigned = sum(a["quantity"] for a in assignments_db if a["base_id"] == base_id)
	expended = sum(e["quantity"] for e in expended_db if e["base_id"] == base_id)
	
	net_movement = purchases + transfer_in - transfer_out
	closing = opening + net_movement - assigned - expended
	
	return {
		"base_id": base_id,
		"opening_balance": opening,
		"purchases": purchases,
		"transfer_in": transfer_in,
		"transfer_out": transfer_out,
		"assigned": assigned,
		"expended": expended,
		"net_movement": net_movement,
		"closing_balance": closing,
	}

# ==================== Bases ====================
@app.get("/api/bases")
def list_bases():
	"""Get all bases"""
	return bases_db

# ==================== Equipment ====================
@app.get("/api/equipment")
def list_equipment():
	"""Get all equipment types"""
	return equipment_db

# ==================== Purchases ====================
@app.post("/api/purchases")
def create_purchase(purchase: PurchaseCreate, token: str = None):
	"""Record a purchase"""
	if token:
		user = verify_token(token)
		check_rbac(user, "logistics_officer", purchase.base_id)
	
	purchase_record = {
		"id": len(purchases_db) + 1,
		"base_id": purchase.base_id,
		"equipment_id": purchase.equipment_id,
		"quantity": purchase.quantity,
		"purchase_date": purchase.purchase_date or datetime.now().isoformat(),
	}
	purchases_db.append(purchase_record)
	return {"ok": True, "message": "Purchase recorded", "data": purchase_record}

@app.get("/api/purchases")
def list_purchases(base_id: Optional[int] = None, equipment_id: Optional[int] = None, token: str = None):
	"""Get purchases with filters"""
	if token:
		user = verify_token(token)
		if user["role"] == "base_commander":
			base_id = user["base_id"]
	
	result = purchases_db
	if base_id:
		result = [p for p in result if p["base_id"] == base_id]
	if equipment_id:
		result = [p for p in result if p["equipment_id"] == equipment_id]
	
	return result

# ==================== Transfers ====================
@app.post("/api/transfers")
def create_transfer(transfer: TransferCreate, token: str = None):
	"""Record an inter-base transfer"""
	if token:
		user = verify_token(token)
		check_rbac(user, "logistics_officer", transfer.from_base_id)
	
	transfer_record = {
		"id": len(transfers_db) + 1,
		"from_base_id": transfer.from_base_id,
		"to_base_id": transfer.to_base_id,
		"equipment_id": transfer.equipment_id,
		"quantity": transfer.quantity,
		"transfer_date": transfer.transfer_date or datetime.now().isoformat(),
	}
	transfers_db.append(transfer_record)
	return {"ok": True, "message": "Transfer recorded", "data": transfer_record}

@app.get("/api/transfers")
def list_transfers(base_id: Optional[int] = None, token: str = None):
	"""Get transfers (both sent and received)"""
	if token:
		user = verify_token(token)
		if user["role"] == "base_commander":
			base_id = user["base_id"]
	
	result = transfers_db
	if base_id:
		result = [t for t in result if t["from_base_id"] == base_id or t["to_base_id"] == base_id]
	
	return result

# ==================== Assignments ====================
@app.post("/api/assignments")
def create_assignment(assignment: AssignmentCreate, token: str = None):
	"""Assign assets to personnel"""
	if token:
		user = verify_token(token)
		check_rbac(user, base_id=assignment.base_id)
	
	assignment_record = {
		"id": len(assignments_db) + 1,
		"base_id": assignment.base_id,
		"equipment_id": assignment.equipment_id,
		"personnel_name": assignment.personnel_name,
		"quantity": assignment.quantity,
		"assigned_date": assignment.assigned_date or datetime.now().isoformat(),
	}
	assignments_db.append(assignment_record)
	return {"ok": True, "message": "Assignment recorded", "data": assignment_record}

@app.get("/api/assignments")
def list_assignments(base_id: Optional[int] = None, token: str = None):
	"""Get assignments"""
	if token:
		user = verify_token(token)
		if user["role"] == "base_commander":
			base_id = user["base_id"]
	
	result = assignments_db
	if base_id:
		result = [a for a in result if a["base_id"] == base_id]
	
	return result

# ==================== Expenditures ====================
@app.post("/api/expenditures")
def create_expenditure(expend: ExpenditureCreate, token: str = None):
	"""Record expended assets"""
	if token:
		user = verify_token(token)
		check_rbac(user, base_id=expend.base_id)
	
	expended_record = {
		"id": len(expended_db) + 1,
		"base_id": expend.base_id,
		"equipment_id": expend.equipment_id,
		"quantity": expend.quantity,
		"expended_date": expend.expended_date or datetime.now().isoformat(),
	}
	expended_db.append(expended_record)
	return {"ok": True, "message": "Expenditure recorded", "data": expended_record}

@app.get("/api/expenditures")
def list_expenditures(base_id: Optional[int] = None, token: str = None):
	"""Get expended assets"""
	if token:
		user = verify_token(token)
		if user["role"] == "base_commander":
			base_id = user["base_id"]
	
	result = expended_db
	if base_id:
		result = [e for e in result if e["base_id"] == base_id]
	
	return result

# ==================== Stock ====================
@app.get("/api/stock")
def get_stock(base_id: int = 1, token: str = None):
	"""Get current stock for a base"""
	if token:
		user = verify_token(token)
		check_rbac(user, base_id=base_id)
	
	return stock_data.get(base_id, {})

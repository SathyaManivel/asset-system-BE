from sqlalchemy import Column, Integer, String, Enum, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base

class BaseModel(Base):
    __tablename__ = "bases"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)

class EquipmentType(Base):
    __tablename__ = "equipment_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("admin", "base_commander", "logistics_officer"))
    base_id = Column(Integer, ForeignKey("bases.id"))

class OpeningStock(Base):
    __tablename__ = "stock_opening"
    id = Column(Integer, primary_key=True)
    base_id = Column(Integer, ForeignKey("bases.id"))
    equipment_id = Column(Integer, ForeignKey("equipment_types.id"))
    quantity = Column(Integer)
    date = Column(Date)

class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True)
    base_id = Column(Integer, ForeignKey("bases.id"))
    equipment_id = Column(Integer, ForeignKey("equipment_types.id"))
    quantity = Column(Integer)
    purchase_date = Column(Date)

class Transfer(Base):
    __tablename__ = "transfers"
    id = Column(Integer, primary_key=True)
    from_base = Column(Integer, ForeignKey("bases.id"))
    to_base = Column(Integer, ForeignKey("bases.id"))
    equipment_id = Column(Integer, ForeignKey("equipment_types.id"))
    quantity = Column(Integer)
    transfer_date = Column(Date)

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True)
    base_id = Column(Integer, ForeignKey("bases.id"))
    equipment_id = Column(Integer, ForeignKey("equipment_types.id"))
    personnel_name = Column(String(150))
    quantity = Column(Integer)
    assigned_date = Column(Date)

class Expended(Base):
    __tablename__ = "expended"
    id = Column(Integer, primary_key=True)
    base_id = Column(Integer, ForeignKey("bases.id"))
    equipment_id = Column(Integer, ForeignKey("equipment_types.id"))
    quantity = Column(Integer)
    expended_date = Column(Date)

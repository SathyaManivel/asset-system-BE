from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models

def get_opening_balance(db: Session, base_id: int, date: str):
    return db.query(func.sum(models.OpeningStock.quantity))\
        .filter(models.OpeningStock.base_id == base_id)\
        .scalar() or 0

def get_total_purchases(db: Session, base_id: int, start_date, end_date):
    q = db.query(func.sum(models.Purchase.quantity))\
        .filter(models.Purchase.base_id == base_id)

    if start_date:
        q = q.filter(models.Purchase.purchase_date >= start_date)
    if end_date:
        q = q.filter(models.Purchase.purchase_date <= end_date)

    return q.scalar() or 0


def get_total_transfer_in(db: Session, base_id: int, start_date, end_date):
    q = db.query(func.sum(models.Transfer.quantity))\
        .filter(models.Transfer.to_base == base_id)

    if start_date: q = q.filter(models.Transfer.transfer_date >= start_date)
    if end_date: q = q.filter(models.Transfer.transfer_date <= end_date)

    return q.scalar() or 0

def get_total_transfer_out(db: Session, base_id: int, start_date, end_date):
    q = db.query(func.sum(models.Transfer.quantity))\
        .filter(models.Transfer.from_base == base_id)

    if start_date: q = q.filter(models.Transfer.transfer_date >= start_date)
    if end_date: q = q.filter(models.Transfer.transfer_date <= end_date)

    return q.scalar() or 0

def get_total_assigned(db: Session, base_id: int, start_date, end_date):
    q = db.query(func.sum(models.Assignment.quantity))\
        .filter(models.Assignment.base_id == base_id)

    if start_date: q = q.filter(models.Assignment.assigned_date >= start_date)
    if end_date: q = q.filter(models.Assignment.assigned_date <= end_date)

    return q.scalar() or 0

def get_total_expended(db: Session, base_id: int, start_date, end_date):
    q = db.query(func.sum(models.Expended.quantity))\
        .filter(models.Expended.base_id == base_id)

    if start_date: q = q.filter(models.Expended.expended_date >= start_date)
    if end_date: q = q.filter(models.Expended.expended_date <= end_date)

    return q.scalar() or 0

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_user
from app import crud

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/")
def get_dashboard_data(
    base_id: int,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Dashboard Metrics:
    - opening_balance
    - purchases
    - transfer_in
    - transfer_out
    - assigned
    - expended
    - closing_balance
    """

    # Restrict Base Commander to only their base
    if current_user["role"] == "base_commander" and current_user["base_id"] != base_id:
        raise HTTPException(status_code=403, detail="Access denied for this base")

    # Get data from CRUD functions
    opening_balance = crud.get_opening_balance(db, base_id, start_date)
    purchases = crud.get_total_purchases(db, base_id, start_date, end_date)
    transfer_in = crud.get_total_transfer_in(db, base_id, start_date, end_date)
    transfer_out = crud.get_total_transfer_out(db, base_id, start_date, end_date)
    assigned = crud.get_total_assigned(db, base_id, start_date, end_date)
    expended = crud.get_total_expended(db, base_id, start_date, end_date)

    # Closing balance calculation
    closing_balance = (
        opening_balance
        + purchases
        + transfer_in
        - transfer_out
        - expended
    )

    # Net movement calculation
    net_movement = purchases + transfer_in - transfer_out

    return {
        "base_id": base_id,
        "opening_balance": opening_balance,
        "purchases": purchases,
        "transfer_in": transfer_in,
        "transfer_out": transfer_out,
        "assigned": assigned,
        "expended": expended,
        "net_movement": net_movement,
        "closing_balance": closing_balance,
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
        },
    }

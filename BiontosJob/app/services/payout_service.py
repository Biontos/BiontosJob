from sqlalchemy.orm import Session
from app.models.payout import Payout

def get_all_payouts(db: Session):
    return db.query(Payout).all()

def approve_payout(db: Session, payout_id: int):
    payout = db.query(Payout).filter(Payout.id == payout_id).first()
    if payout:
        payout.status = "approved"
        db.commit()
    return payout

def cancel_payout(db: Session, payout_id: int):
    payout = db.query(Payout).filter(Payout.id == payout_id).first()
    if payout:
        payout.status = "canceled"
        db.commit()
    return payout

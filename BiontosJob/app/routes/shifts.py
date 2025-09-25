from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.shift import Shift

router = APIRouter()

@router.get("/")
def get_shifts(db: Session = Depends(get_db)):
    return db.query(Shift).all()

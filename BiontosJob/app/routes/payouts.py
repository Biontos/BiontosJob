# app/routers/payout.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.payout_service import get_all_payouts
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/payouts", tags=["payouts"])

templates = Jinja2Templates(directory="frontend/templates")

@router.get("/api")
def get_payouts_api(db: Session = Depends(get_db)):
    return get_all_payouts(db)


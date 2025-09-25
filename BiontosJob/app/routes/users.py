from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User

router = APIRouter()

@router.get("/")
async def get_users():
    return {"message": "Users endpoint"}

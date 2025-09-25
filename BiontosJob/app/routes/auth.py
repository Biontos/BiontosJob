from fastapi import APIRouter, Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
import shutil, os
from app.database import get_db
from app.models.user import User
from app.utils.security import hash_password, verify_password

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

UPLOAD_DIR = "frontend/static/img/profiles"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ======= Регистрация =======
@router.get("/auth/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request, "error": None})


@router.post("/auth/register", response_class=HTMLResponse)
def register_form(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "Email уже зарегистрирован"}
        )

    user = User(full_name=full_name, email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return RedirectResponse("/auth/login", status_code=303)


# ======= Логин =======
@router.get("/auth/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request, "error": None})


@router.post("/auth/login", response_class=HTMLResponse)
def login_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Неверный email или пароль"}
        )

    request.session["user_id"] = user.id
    request.session["email"] = user.email
    return RedirectResponse("/profile", status_code=303)


# ======= Логаут =======
@router.get("/auth/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


# ======= Профиль =======
@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/auth/login", status_code=303)

    user = db.query(User).filter(User.id == user_id).first()
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "profile_image": user.profile_image
        }
    )


@router.post("/profile/upload")
async def upload_profile_image(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/auth/login", status_code=303)

    try:
        filename = f"user_{user_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return RedirectResponse("/auth/login", status_code=303)

        user.profile_image = filename
        db.commit()
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return templates.TemplateResponse(
            "profile.html",
            {
                "request": request,
                "user_id": user_id,
                "email": request.session.get("email"),
                "full_name": user.full_name,
                "profile_image": user.profile_image,
                "error": "Ошибка при загрузке файла"
            }
        )

    return RedirectResponse("/profile", status_code=303)

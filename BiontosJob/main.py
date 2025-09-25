import os
import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from app.routes import auth, users

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(debug=True)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "supersecret")
)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

templates = Jinja2Templates(directory="frontend/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    logger.debug("Accessing root endpoint")
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user_id = request.session.get("user_id")
    logger.debug(f"Accessing dashboard for user_id: {user_id}")
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user_id": user_id}
    )

app.include_router(auth.router)
app.include_router(users.router, prefix="/users", tags=["users"])
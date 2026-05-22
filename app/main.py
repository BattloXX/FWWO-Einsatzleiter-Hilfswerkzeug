"""FastAPI application – Einsatzleiter-Hilfswerkzeug FF Wolfurt."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db import SessionLocal, engine
from app.core.security import unsign_session
from app.models.user import User

from app.routers import auth, api_v1, ws
from app.routers import ui_incident, ui_breathing, ui_archive, ui_admin, ui_stats, ui_push


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Bootstrap admin on first start
    _bootstrap_admin()
    yield


def _bootstrap_admin() -> None:
    db = SessionLocal()
    try:
        from app.models.user import User as U
        existing = db.query(U).first()
        if existing:
            return
        from app.seed_data import seed
        seed(db)
        from app.cli import create_admin
        create_admin(settings.BOOTSTRAP_ADMIN_USER, settings.BOOTSTRAP_ADMIN_PASSWORD)
    finally:
        db.close()


app = FastAPI(
    title="Einsatzleiter-Hilfswerkzeug FF Wolfurt",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url=None,
    lifespan=lifespan,
)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Session middleware – inject request.state.user
@app.middleware("http")
async def session_middleware(request: Request, call_next):
    token = request.cookies.get("session")
    request.state.user = None
    if token:
        user_id = unsign_session(token)
        if user_id:
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id, User.active == True).first()  # noqa: E712
                request.state.user = user
            finally:
                db.close()
    return await call_next(request)


# Routers
app.include_router(auth.router)
app.include_router(api_v1.router)
app.include_router(ws.router)
app.include_router(ui_incident.router)
app.include_router(ui_breathing.router)
app.include_router(ui_archive.router)
app.include_router(ui_admin.router)
app.include_router(ui_stats.router)
app.include_router(ui_push.router)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse("/static/img/favicon.ico")

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.staticfiles import StaticFiles
import os

from core.config import settings
# from db.database import engine
# from db.base import Base

# Import all models so SQLAlchemy registers them before create_all
from models import appointment, doctor, user, doctor_availability, doctor_favorite, doctor_review, category  # noqa: F401, E402
from routers import appointments, auth, users, category, doctor, doctor_availability, doctor_review


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Doctor Finder API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, "CORS_ORIGINS", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
os.makedirs("image/category", exist_ok=True)
os.makedirs("image/doctor", exist_ok=True)

app.mount(
    "/image",
    StaticFiles(directory="image"),
    name="image"
)
app.mount(
    "/image",
    StaticFiles(directory="image"),
    name="image"
)

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(appointments.router)
app.include_router(category.router)
app.include_router(doctor_review.router)
app.include_router(doctor_availability.router)
app.include_router(doctor.router)

# Health Check Routes
@app.get("/", tags=["Health"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


# ============================================================
# RUN 
# python main.py
# kill -9 $(lsof -t -i :8000)
# python -m alembic revision --autogenerate -m "describe your change"
# python -m alembic upgrade head
# ============================================================

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

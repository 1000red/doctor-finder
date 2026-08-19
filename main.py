from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.config import settings
from db.database import engine
from db.base import Base

# Import all models so SQLAlchemy registers them before create_all
from models import user, docrot, doctor_availability, doctor_favorite, doctor_review, category  # noqa: F401, E402
from routers import auth, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database initialization
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Failed to create database tables: {e}")
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

# Routers
app.include_router(auth.router)
app.include_router(users.router)


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
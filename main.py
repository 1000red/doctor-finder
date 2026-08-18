from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from db.database import engine
from db import base

# Import models so SQLAlchemy knows about the tables
from models import user  # noqa: F401

# Import routers
from routers import auth, users


# ============================================================
# DATABASE
# ============================================================

try:
    base.Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

except Exception as e:
    print(f"Failed to create database tables: {e}")


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Doctor Finder API",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth.router)
app.include_router(users.router)


# ============================================================
# HEALTH CHECK
# ============================================================

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
    return {
        "status": "ok",
    }


# ============================================================
# RUN python main.py
# kill -9 $(lsof -t -i :8000)
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.core import settings
from app.config.database import sessionmanager
from app.routers.halal_check import router as halal_check_router
from app.utils.database import BaseDB

# Import models to register them with SQLAlchemy
from app.models import halal_check  # noqa: F401

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("lifespan")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up: creating DB tables if not exist")
    async with sessionmanager._engine.begin() as conn:
        await conn.run_sync(BaseDB.metadata.create_all)

    yield

    logger.info("Shutting down: disposing DB engine")
    await sessionmanager.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Halal Compliance Checker API using Google Gemini AI",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "http://frontend:80",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(halal_check_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "healthy",
        "service": "Halal Checker API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "database": "connected"
    }



import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.config import settings
from core.database import init_db, close_db, init_redis, close_redis
from api.v1 import v1_router
import time

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"LLM Mode: {settings.LLM_ROUTER_MODEL}")
    logger.info(f"Database: {settings.DATABASE_URL}")
    await init_db()
    await init_redis()
    yield
    await close_db()
    await close_redis()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Autonomous Freight Operating System for UAE and GCC",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    process_time = time.time() - start
    response.headers["X-Process-Time-MS"] = str(int(process_time * 1000))
    return response


@app.middleware("http")
async def error_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(e) if settings.DEBUG else None},
        )


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
        "llm": settings.LLM_ROUTER_MODEL,
        "ollama_url": settings.OLLAMA_BASE_URL,
    }


@app.get("/setup")
async def setup_check():
    """Check what's configured and working."""
    checks = {
        "ollama_available": False,
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "database": "sqlite" if "sqlite" in settings.DATABASE_URL else "postgresql",
    }
    # Check if Ollama is running
    try:
        import httpx
        async with httpx.AsyncClient(timeout=2) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                checks["ollama_available"] = True
                checks["ollama_models"] = [m["name"] for m in models]
    except:
        checks["ollama_available"] = False
        checks["ollama_hint"] = "Install Ollama: https://ollama.ai  then: ollama pull mistral"

    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
        "checks": checks,
    }


app.include_router(v1_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "setup_check": "/setup",
        "health": "/health",
    }

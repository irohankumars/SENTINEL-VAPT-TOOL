import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from .config import settings
from .database import init_db
from .routers import projects, scans, findings, reports, dashboard

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="SentinelVAPT API",version="0.1.0",description="Beginner-friendly orchestration API for authorized web security assessments.",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(projects.router,prefix="/api")
app.include_router(scans.router,prefix="/api")
app.include_router(findings.router,prefix="/api")
app.include_router(reports.router,prefix="/api")
app.include_router(dashboard.router,prefix="/api")

@app.middleware("http")
async def security_headers(request: Request, call_next):
    if request.headers.get("content-length") and int(request.headers["content-length"]) > 1_000_000:
        return JSONResponse(status_code=413, content={"detail":"Request body is too large"})
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response

@app.get("/api/health",tags=["System"],summary="Check API readiness")
def health(): return {"status":"online","mock_scanners":settings.mock_scanners}

@app.exception_handler(SQLAlchemyError)
async def database_error(request: Request, exc: SQLAlchemyError):
    logger.exception("Database error on %s", request.url.path)
    return JSONResponse(status_code=500,content={"detail":"Database operation failed"})

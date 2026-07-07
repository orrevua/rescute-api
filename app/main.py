import logging
import os
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.adapters.inbound.api.router import router
from app.rate_limit import limiter

_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
}


def _is_production() -> bool:
    return os.getenv("ENVIRONMENT", "").lower() == "production"


def _cors_origins() -> list[str]:
    origins: list[str] = []
    if not _is_production():
        origins.extend(["http://localhost:3000", "http://127.0.0.1:3000"])
    if frontend := os.getenv("FRONTEND_URL"):
        origins.append(frontend.rstrip("/"))
    return origins


log = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parent.parent


def _run_migrations() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        log.info("Database migrations applied")
    else:
        log.error("Migration failed: %s", result.stderr)


async def _seed_demo_data() -> None:
    from scripts.seed import seed

    try:
        await seed()
        log.info("Demo seed ensured")
    except Exception as error:  # noqa: BLE001 — seed failure must not block startup
        log.error("Demo seed failed: %s", error)


@asynccontextmanager
async def _lifespan(app: FastAPI):
    if os.getenv("RUN_MIGRATIONS_ON_STARTUP", "1") == "1":
        _run_migrations()
    if os.getenv("SEED_DEMO_DATA", "1") == "1":
        await _seed_demo_data()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Rescute API", version="0.1.0", lifespan=_lifespan)

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        for header, value in _SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)
        if request.url.path.startswith("/uploads/"):
            response.headers["Content-Disposition"] = "attachment"
        return response

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(router, prefix="/api/v1")

    os.makedirs("uploads", exist_ok=True)
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    return app


app = create_app()
